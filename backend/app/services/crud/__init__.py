"""
CRUD Services Package

Exports all CRUD operations for database entities.
"""

from app.services.crud.user import (
    get_user,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    update_user_role,
    update_user_password,
    verify_user,
    deactivate_user,
    activate_user,
    delete_user,
    search_users,
    count_users,
)

from app.services.crud.resource import (
    get_resource,
    get_resource_by_slug,
    get_resources,
    create_resource,
    update_resource,
    delete_resource,
    get_resources_by_tags,
    count_resources,
)

from app.services.crud.progress import (
    get_progress,
    get_user_progress,
    get_user_all_progress,
    create_progress,
    update_progress,
    upsert_progress,
    delete_progress,
    get_completion_stats,
)

from app.services.crud.interview import (
    get_session,
    get_user_sessions,
    create_session,
    update_session,
    start_session,
    complete_session,
    archive_session,
    add_question,
    add_response,
    delete_session,
    get_session_stats,
)

from app.services.crud.analysis import (
    get_analysis,
    get_analysis_by_session,
    create_analysis,
    update_analysis,
    append_verbal_metrics,
    append_nonverbal_metrics,
    update_multimodal_score,
    add_recommendations,
    delete_analysis,
    get_user_analyses,
    get_average_scores,
)

__all__ = [
    # User CRUD
    "get_user",
    "get_user_by_email",
    "get_users",
    "create_user",
    "update_user",
    "update_user_role",
    "update_user_password",
    "verify_user",
    "deactivate_user",
    "activate_user",
    "delete_user",
    "search_users",
    "count_users",
    # Resource CRUD
    "get_resource",
    "get_resource_by_slug",
    "get_resources",
    "create_resource",
    "update_resource",
    "delete_resource",
    "get_resources_by_tags",
    "count_resources",
    # Progress CRUD
    "get_progress",
    "get_user_progress",
    "get_user_all_progress",
    "create_progress",
    "update_progress",
    "upsert_progress",
    "delete_progress",
    "get_completion_stats",
    # Interview CRUD
    "get_session",
    "get_user_sessions",
    "create_session",
    "update_session",
    "start_session",
    "complete_session",
    "archive_session",
    "add_question",
    "add_response",
    "delete_session",
    "get_session_stats",
    # Analysis CRUD
    "get_analysis",
    "get_analysis_by_session",
    "create_analysis",
    "update_analysis",
    "append_verbal_metrics",
    "append_nonverbal_metrics",
    "update_multimodal_score",
    "add_recommendations",
    "delete_analysis",
    "get_user_analyses",
    "get_average_scores",
]
