/**
 * WebRTC Signaling Server
 * Handles peer connection signaling for real-time video
 */
const WebSocket = require('ws');

const PORT = process.env.SIGNALING_PORT || 8080;

const wss = new WebSocket.Server({ port: PORT });

// Store active rooms
const rooms = new Map();

wss.on('connection', (ws) => {
    console.log('New client connected');

    let currentRoom = null;
    let clientId = null;

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);

            switch (data.type) {
                case 'join':
                    handleJoin(ws, data, (room, id) => {
                        currentRoom = room;
                        clientId = id;
                    });
                    break;

                case 'offer':
                case 'answer':
                case 'ice-candidate':
                    handleSignaling(ws, data, currentRoom);
                    break;

                case 'leave':
                    handleLeave(ws, currentRoom, clientId);
                    break;
            }
        } catch (error) {
            console.error('Error processing message:', error);
        }
    });

    ws.on('close', () => {
        if (currentRoom && clientId) {
            handleLeave(ws, currentRoom, clientId);
        }
        console.log('Client disconnected');
    });
});

function handleJoin(ws, data, callback) {
    const { roomId, clientId } = data;

    if (!rooms.has(roomId)) {
        rooms.set(roomId, new Map());
    }

    const room = rooms.get(roomId);
    room.set(clientId, ws);

    // Notify existing peers
    room.forEach((peerWs, peerId) => {
        if (peerId !== clientId) {
            peerWs.send(JSON.stringify({
                type: 'peer-joined',
                peerId: clientId
            }));
        }
    });

    callback(roomId, clientId);
}

function handleSignaling(ws, data, roomId) {
    if (!roomId || !rooms.has(roomId)) return;

    const room = rooms.get(roomId);
    const targetWs = room.get(data.targetId);

    if (targetWs) {
        targetWs.send(JSON.stringify(data));
    }
}

function handleLeave(ws, roomId, clientId) {
    if (!roomId || !rooms.has(roomId)) return;

    const room = rooms.get(roomId);
    room.delete(clientId);

    // Notify remaining peers
    room.forEach((peerWs) => {
        peerWs.send(JSON.stringify({
            type: 'peer-left',
            peerId: clientId
        }));
    });

    if (room.size === 0) {
        rooms.delete(roomId);
    }
}

console.log(`Signaling server running on port ${PORT}`);
