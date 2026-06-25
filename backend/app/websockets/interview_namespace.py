import socketio
from typing import Any, Dict
from app.tasks.pipeline_tasks import celery_app
# In production, we'd process audio/video frames using background tasks or streaming them to a message queue.

class InterviewNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        """Handle client connection to the interview namespace."""
        print(f"Client {sid} connected to /interview namespace")
        # Example: validate session_id and user auth
        # session_id = auth.get('session_id')
        # if not session_id:
        #     raise socketio.exceptions.ConnectionRefusedError('session_id required')
        # self.enter_room(sid, session_id)
        return True

    async def on_disconnect(self, sid):
        """Handle client disconnection."""
        print(f"Client {sid} disconnected from /interview namespace")

    async def on_video_frame(self, sid, data: Dict[str, Any]):
        """Handle incoming video frames."""
        session_id = data.get('session_id')
        frame_base64 = data.get('frame_base64')
        timestamp_ms = data.get('timestamp_ms')
        if not session_id or not frame_base64: return
        celery_app.send_task(
            'app.tasks.vision_tasks.process_video_chunk',
            args=[session_id, timestamp_ms, frame_base64],
            queue='vision'
        )
        
    async def on_audio_chunk(self, sid, data: Dict[str, Any]):
        """Handle incoming audio chunks."""
        session_id = data.get('session_id')
        audio_data = data.get('audio_data')
        timestamp_ms = data.get('timestamp_ms')
        if not session_id or not audio_data: return
        celery_app.send_task(
            'app.tasks.speech_tasks.process_audio_chunk',
            args=[session_id, timestamp_ms, audio_data],
            queue='speech'
        )

    async def on_start_interview_flow(self, sid, data: Dict[str, Any]):
        """Starts the active interview loop and retrieves the first question."""
        session_id = data.get('session_id')
        if not session_id: return
        
        # Join the session room for targeted events like coaching_hints
        self.enter_room(sid, session_id)
        
        from app.core.database import AsyncSessionLocal
        from app.services.orchestrator import InterviewOrchestrator
        
        async with AsyncSessionLocal() as db:
            orchestrator = InterviewOrchestrator(db)
            try:
                result = await orchestrator.start_session(session_id)
                await self.emit('question_delivered', result, room=sid)
            except Exception as e:
                await self.emit('error', {'message': str(e)}, room=sid)

    async def on_submit_answer(self, sid, data: Dict[str, Any]):
        """Receives candidate answer transcript, evaluates it, and generates next question."""
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        transcript = data.get('transcript')
        
        if not all([session_id, question_id, transcript]): return
        
        from app.core.database import AsyncSessionLocal
        from app.services.orchestrator import InterviewOrchestrator
        
        async with AsyncSessionLocal() as db:
            orchestrator = InterviewOrchestrator(db)
            try:
                result = await orchestrator.process_answer(session_id, question_id, transcript)
                await self.emit('evaluation_and_next_question', result, room=sid)
            except Exception as e:
                await self.emit('error', {'message': str(e)}, room=sid)

    async def on_end_session(self, sid, data: Dict[str, Any]):
        """Handle the end of an interview session."""
        session_id = data.get('session_id')
        if session_id:
            celery_app.send_task(
                'app.tasks.pipeline_tasks.generate_report_task',
                args=[session_id],
                queue='pipeline'
            )
            await self.emit('session_ended', {'status': 'processing'}, room=sid)

def register_namespaces(sio: socketio.AsyncServer):
    """Register all Socket.IO namespaces"""
    sio.register_namespace(InterviewNamespace('/interview'))
