import os
import logging
from typing import Optional, List, Dict, Any
import gitlab
import gitlab.exceptions
from gitlab.v4.objects import Project, Issue, MergeRequest
from pydantic import BaseModel, Field
from .git_detector import GitDetector
from .constants import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    SMALL_PAGE_SIZE,
    DEFAULT_MAX_BODY_LENGTH,
    DEFAULT_GITLAB_URL,
    CACHE_TTL_MEDIUM,
    CACHE_TTL_LONG
)
from .utils import timed_cache, retry_on_error

logger = logging.getLogger(__name__)


class GitLabConfig(BaseModel):
    url: str = Field(default="https://gitlab.com", description="GitLab instance URL")
    private_token: Optional[str] = Field(default=None, description="GitLab private token")
    oauth_token: Optional[str] = Field(default=None, description="GitLab OAuth token")


class GitLabClient:
    def __init__(self, config: GitLabConfig):
        self.config = config
        self.gl = None
        self._initialize_client()
    
    def _initialize_client(self):
        auth_kwargs = {}
        
        if self.config.private_token:
            auth_kwargs['private_token'] = self.config.private_token
        elif self.config.oauth_token:
            auth_kwargs['oauth_token'] = self.config.oauth_token
        else:
            raise ValueError("Either private_token or oauth_token must be provided")
        
        self.gl = gitlab.Gitlab(self.config.url, **auth_kwargs)
        self.gl.auth()
    
    @retry_on_error()
    def get_projects(self, owned: bool = False, membership: bool = True, search: Optional[str] = None,
                    per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get accessible projects with pagination"""
        kwargs = {
            'owned': owned,
            'membership': membership,
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),
            'page': page
        }
        if search:
            kwargs['search'] = search
        
        projects_response = self.gl.projects.list(**kwargs)
        
        # Extract pagination info
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(projects_response.total) if hasattr(projects_response, 'total') and projects_response.total is not None else None,
            'total_pages': int(projects_response.total_pages) if hasattr(projects_response, 'total_pages') and projects_response.total_pages is not None else None,
            'next_page': int(projects_response.next_page) if hasattr(projects_response, 'next_page') and projects_response.next_page is not None else None,
            'prev_page': int(projects_response.prev_page) if hasattr(projects_response, 'prev_page') and projects_response.prev_page is not None else None
        }
        
        return {
            'projects': [self._project_to_dict(p) for p in projects_response],
            'pagination': pagination_info
        }
    
    @timed_cache(seconds=CACHE_TTL_LONG)
    @retry_on_error()
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID or path"""
        project = self.gl.projects.get(project_id)
        return self._project_to_dict(project)
    
    @retry_on_error()
    def get_project_members(self, project_id: str, query: Optional[str] = None,
                           per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get project members with their access levels"""
        project = self.gl.projects.get(project_id)
        
        kwargs = {'get_all': False, 'per_page': per_page, 'page': page}
        if query:
            kwargs['query'] = query
            
        members_response = project.members.list(**kwargs)
        
        members = []
        for member in members_response:
            members.append({
                'id': member.id,
                'username': member.username,
                'name': member.name,
                'state': member.state,
                'avatar_url': getattr(member, 'avatar_url', None),
                'web_url': getattr(member, 'web_url', None),
                'access_level': member.access_level,
                'access_level_name': self._access_level_to_string(member.access_level),
                'expires_at': getattr(member, 'expires_at', None),
                'created_at': member.created_at
            })
            
        # Extract pagination info
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(members_response.total) if hasattr(members_response, 'total') and members_response.total is not None else None,
            'total_pages': int(members_response.total_pages) if hasattr(members_response, 'total_pages') and members_response.total_pages is not None else None,
            'next_page': int(members_response.next_page) if hasattr(members_response, 'next_page') and members_response.next_page is not None else None,
            'prev_page': int(members_response.prev_page) if hasattr(members_response, 'prev_page') and members_response.prev_page is not None else None
        }
            
        return {
            'members': members,
            'pagination': pagination_info
        }
    
    @retry_on_error()
    def get_project_hooks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get project webhooks"""
        project = self.gl.projects.get(project_id)
        hooks = project.hooks.list(get_all=False, per_page=DEFAULT_PAGE_SIZE)
        
        return [{
            'id': hook.id,
            'url': hook.url,
            'created_at': hook.created_at,
            'push_events': getattr(hook, 'push_events', False),
            'tag_push_events': getattr(hook, 'tag_push_events', False),
            'merge_requests_events': getattr(hook, 'merge_requests_events', False),
            'repository_update_events': getattr(hook, 'repository_update_events', False),
            'wiki_page_events': getattr(hook, 'wiki_page_events', False),
            'issues_events': getattr(hook, 'issues_events', False),
            'confidential_issues_events': getattr(hook, 'confidential_issues_events', False),
            'note_events': getattr(hook, 'note_events', False),
            'pipeline_events': getattr(hook, 'pipeline_events', False),
            'job_events': getattr(hook, 'job_events', False),
            'deployment_events': getattr(hook, 'deployment_events', False),
            'releases_events': getattr(hook, 'releases_events', False),
            'enable_ssl_verification': getattr(hook, 'enable_ssl_verification', True),
            'token': '[REDACTED]' if hasattr(hook, 'token') and hook.token else None,
            'push_events_branch_filter': getattr(hook, 'push_events_branch_filter', None),
            'alert_status': getattr(hook, 'alert_status', None)
        } for hook in hooks]
    
    @retry_on_error()
    def get_issues(self, project_id: str, state: str = "opened", 
                  per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get issues for a project with pagination"""
        project = self.gl.projects.get(project_id)
        
        kwargs = {
            'state': state,
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),
            'page': page
        }
        
        issues_response = project.issues.list(**kwargs)
        
        # Extract pagination info
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(issues_response.total) if hasattr(issues_response, 'total') and issues_response.total is not None else None,
            'total_pages': int(issues_response.total_pages) if hasattr(issues_response, 'total_pages') and issues_response.total_pages is not None else None,
            'next_page': int(issues_response.next_page) if hasattr(issues_response, 'next_page') and issues_response.next_page is not None else None,
            'prev_page': int(issues_response.prev_page) if hasattr(issues_response, 'prev_page') and issues_response.prev_page is not None else None
        }
        
        return {
            'issues': [self._issue_to_dict(issue) for issue in issues_response],
            'pagination': pagination_info,
            'project_id': project_id
        }
    
    @retry_on_error()
    def get_merge_requests(self, project_id: str, state: str = "opened",
                          per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get merge requests for a project with pagination"""
        project = self.gl.projects.get(project_id)
        
        kwargs = {
            'state': state,
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),
            'page': page
        }
        
        mrs_response = project.mergerequests.list(**kwargs)
        
        # Extract pagination info
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(mrs_response.total) if hasattr(mrs_response, 'total') and mrs_response.total is not None else None,
            'total_pages': int(mrs_response.total_pages) if hasattr(mrs_response, 'total_pages') and mrs_response.total_pages is not None else None,
            'next_page': int(mrs_response.next_page) if hasattr(mrs_response, 'next_page') and mrs_response.next_page is not None else None,
            'prev_page': int(mrs_response.prev_page) if hasattr(mrs_response, 'prev_page') and mrs_response.prev_page is not None else None
        }
        
        return {
            'merge_requests': [self._mr_to_dict(mr) for mr in mrs_response],
            'pagination': pagination_info,
            'project_id': project_id
        }
    
    def create_issue(self, project_id: str, title: str, description: Optional[str] = None,
                    labels: Optional[List[str]] = None, assignee_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Create a new issue"""
        project = self.gl.projects.get(project_id)
        issue_data = {'title': title}
        
        if description:
            issue_data['description'] = description
        if labels:
            issue_data['labels'] = labels
        if assignee_ids:
            issue_data['assignee_ids'] = assignee_ids
        
        issue = project.issues.create(issue_data)
        return self._issue_to_dict(issue)
    
    def add_issue_comment(self, project_id: str, issue_iid: int, body: str) -> Dict[str, Any]:
        """Add a comment to an issue"""
        project = self.gl.projects.get(project_id)
        issue = project.issues.get(issue_iid)
        note = issue.notes.create({'body': body})
        
        return {
            'id': note.id,
            'body': note.body,
            'author': note.author,
            'created_at': note.created_at,
            'updated_at': note.updated_at,
            'system': getattr(note, 'system', False),
            'noteable_type': 'Issue',
            'noteable_id': issue.id,
            'noteable_iid': issue.iid
        }
    
    def create_merge_request(self, project_id: str, source_branch: str, target_branch: str,
                           title: str, description: Optional[str] = None,
                           remove_source_branch: bool = True) -> Dict[str, Any]:
        """Create a new merge request"""
        project = self.gl.projects.get(project_id)
        mr_data = {
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': title,
            'remove_source_branch': remove_source_branch
        }
        
        if description:
            mr_data['description'] = description
        
        mr = project.mergerequests.create(mr_data)
        return self._mr_to_dict(mr)
    
    def update_merge_request(self, project_id: str, mr_iid: int, **kwargs) -> Dict[str, Any]:
        """Update a merge request with provided fields"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'assignee_id', 'assignee_ids', 
                         'reviewer_ids', 'labels', 'milestone_id', 'state_event',
                         'remove_source_branch', 'squash', 'discussion_locked',
                         'allow_collaboration', 'target_branch']
        
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if update_data:
            for key, value in update_data.items():
                setattr(mr, key, value)
            mr.save()
        
        return self._mr_to_dict(mr)
    
    def close_merge_request(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Close a merge request"""
        return self.update_merge_request(project_id, mr_iid, state_event='close')
    
    def merge_merge_request(self, project_id: str, mr_iid: int, 
                           merge_when_pipeline_succeeds: bool = False,
                           should_remove_source_branch: Optional[bool] = None,
                           merge_commit_message: Optional[str] = None,
                           squash_commit_message: Optional[str] = None,
                           squash: Optional[bool] = None) -> Dict[str, Any]:
        """Merge a merge request"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        merge_params = {}
        if merge_when_pipeline_succeeds:
            merge_params['merge_when_pipeline_succeeds'] = True
        if should_remove_source_branch is not None:
            merge_params['should_remove_source_branch'] = should_remove_source_branch
        if merge_commit_message:
            merge_params['merge_commit_message'] = merge_commit_message
        if squash_commit_message:
            merge_params['squash_commit_message'] = squash_commit_message
        if squash is not None:
            merge_params['squash'] = squash
            
        mr.merge(**merge_params)
        
        # Refresh to get updated state
        mr = project.mergerequests.get(mr_iid)
        return self._mr_to_dict(mr)
    
    def add_merge_request_comment(self, project_id: str, mr_iid: int, body: str) -> Dict[str, Any]:
        """Add a comment to a merge request"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        note = mr.notes.create({'body': body})
        
        return {
            'id': note.id,
            'body': note.body,
            'author': note.author,
            'created_at': note.created_at,
            'updated_at': note.updated_at,
            'system': getattr(note, 'system', False),
            'noteable_type': 'MergeRequest',
            'noteable_id': mr.id,
            'noteable_iid': mr.iid
        }
    
    def approve_merge_request(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Approve a merge request"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        mr.approve()
        
        # Get updated approval state
        approvals = self.get_merge_request_approvals(project_id, mr_iid)
        return {
            'approved': True,
            'approvals': approvals
        }
    
    def get_merge_request_approvals(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Get approval status for a merge request"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        # Get approval state
        approval_state = mr.approval_state.get()
        
        return {
            'approvals_required': getattr(approval_state, 'approvals_required', 0),
            'approvals_left': getattr(approval_state, 'approvals_left', 0),
            'approved_by': [
                {
                    'user': {
                        'id': approval.user.get('id'),
                        'username': approval.user.get('username'),
                        'name': approval.user.get('name')
                    }
                } for approval in getattr(approval_state, 'approved_by', [])
            ],
            'approved': getattr(approval_state, 'approved', False),
            'approval_rules_left': getattr(approval_state, 'approval_rules_left', []),
            'has_approval_rules': hasattr(approval_state, 'approval_rules_left') and len(approval_state.approval_rules_left) > 0
        }
    
    @retry_on_error()
    def get_merge_request_discussions(self, project_id: str, mr_iid: int,
                                    per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Get all discussions for a merge request"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        kwargs = {'get_all': False, 'per_page': per_page, 'page': page}
        discussions_response = mr.discussions.list(**kwargs)
        
        discussions = []
        for discussion in discussions_response:
            disc_dict = {
                'id': discussion.id,
                'individual_note': getattr(discussion, 'individual_note', False),
                'notes': []
            }
            
            for note in discussion.attributes.get('notes', []):
                disc_dict['notes'].append({
                    'id': note.get('id'),
                    'type': note.get('type'),
                    'body': note.get('body'),
                    'author': note.get('author'),
                    'created_at': note.get('created_at'),
                    'updated_at': note.get('updated_at'),
                    'system': note.get('system', False),
                    'noteable_id': note.get('noteable_id'),
                    'noteable_type': note.get('noteable_type'),
                    'resolvable': note.get('resolvable', False),
                    'resolved': note.get('resolved', False),
                    'resolved_by': note.get('resolved_by'),
                    'resolved_at': note.get('resolved_at'),
                    'position': note.get('position'),  # For diff discussions
                    'line_code': note.get('line_code') if note.get('position') else None
                })
            
            discussions.append(disc_dict)
        
        # Extract pagination info
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(discussions_response.total) if hasattr(discussions_response, 'total') and discussions_response.total is not None else None,
            'total_pages': int(discussions_response.total_pages) if hasattr(discussions_response, 'total_pages') and discussions_response.total_pages is not None else None,
            'next_page': int(discussions_response.next_page) if hasattr(discussions_response, 'next_page') and discussions_response.next_page is not None else None,
            'prev_page': int(discussions_response.prev_page) if hasattr(discussions_response, 'prev_page') and discussions_response.prev_page is not None else None
        }
        
        return {
            'discussions': discussions,
            'pagination': pagination_info,
            'merge_request': {
                'iid': mr.iid,
                'title': mr.title,
                'web_url': mr.web_url
            }
        }
    
    def resolve_discussion(self, project_id: str, mr_iid: int, discussion_id: str) -> Dict[str, Any]:
        """Resolve a discussion thread"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        discussion = mr.discussions.get(discussion_id)
        
        # Resolve all resolvable notes in the discussion
        resolved_notes = []
        for note in discussion.attributes.get('notes', []):
            if note.get('resolvable') and not note.get('resolved'):
                note_obj = discussion.notes.get(note['id'])
                note_obj.resolved = True
                note_obj.save()
                resolved_notes.append(note['id'])
        
        return {
            'discussion_id': discussion_id,
            'resolved': True,
            'resolved_notes': resolved_notes
        }
    
    def get_merge_request_changes(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Get file changes for a merge request"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        # Get the changes
        changes = mr.changes()
        
        return {
            'merge_request': {
                'iid': mr.iid,
                'title': changes.get('title'),
                'state': changes.get('state'),
                'source_branch': changes.get('source_branch'),
                'target_branch': changes.get('target_branch'),
                'web_url': changes.get('web_url')
            },
            'changes': [
                {
                    'old_path': change.get('old_path'),
                    'new_path': change.get('new_path'),
                    'a_mode': change.get('a_mode'),
                    'b_mode': change.get('b_mode'),
                    'new_file': change.get('new_file', False),
                    'renamed_file': change.get('renamed_file', False),
                    'deleted_file': change.get('deleted_file', False),
                    'diff': change.get('diff', '')
                } for change in changes.get('changes', [])
            ],
            'overflow': changes.get('overflow', False),
            'diff_refs': changes.get('diff_refs', {})
        }
    
    def rebase_merge_request(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Rebase a merge request onto its target branch"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        # Trigger rebase
        mr.rebase()
        
        # Get updated MR info
        mr = project.mergerequests.get(mr_iid)
        return {
            'merge_request': self._mr_to_dict(mr),
            'rebase_in_progress': getattr(mr, 'rebase_in_progress', False),
            'merge_error': getattr(mr, 'merge_error', None)
        }
    
    def cherry_pick_commit(self, project_id: str, commit_sha: str, branch: str) -> Dict[str, Any]:
        """Cherry-pick a commit to a branch"""
        project = self.gl.projects.get(project_id)
        commit = project.commits.get(commit_sha)
        
        # Cherry-pick the commit
        result = commit.cherry_pick(branch=branch)
        
        return self._commit_to_dict(result)
    
    @retry_on_error()
    def get_pipelines(self, project_id: str, ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pipelines for a project"""
        project = self.gl.projects.get(project_id)
        kwargs = {'get_all': False, 'per_page': SMALL_PAGE_SIZE}
        if ref:
            kwargs['ref'] = ref
        
        pipelines = project.pipelines.list(**kwargs)
        return [self._pipeline_to_dict(p) for p in pipelines]
    
    @timed_cache(seconds=CACHE_TTL_MEDIUM)
    @retry_on_error()
    def get_branches(self, project_id: str) -> List[Dict[str, Any]]:
        """Get branches for a project"""
        project = self.gl.projects.get(project_id)
        branches = project.branches.list(get_all=False, per_page=DEFAULT_PAGE_SIZE)
        return [self._branch_to_dict(b) for b in branches]
    
    @timed_cache(seconds=CACHE_TTL_MEDIUM)
    @retry_on_error()
    def get_tags(self, project_id: str, order_by: str = 'updated', sort: str = 'desc') -> List[Dict[str, Any]]:
        """Get tags for a project"""
        project = self.gl.projects.get(project_id)
        tags = project.tags.list(get_all=False, per_page=DEFAULT_PAGE_SIZE, order_by=order_by, sort=sort)
        
        return [
            {
                'name': tag.name,
                'message': getattr(tag, 'message', ''),
                'target': tag.target,
                'commit': {
                    'id': tag.commit.get('id'),
                    'short_id': tag.commit.get('short_id'),
                    'title': tag.commit.get('title'),
                    'created_at': tag.commit.get('created_at'),
                    'author_name': tag.commit.get('author_name'),
                    'author_email': tag.commit.get('author_email')
                } if hasattr(tag, 'commit') else None,
                'release': {
                    'tag_name': tag.release.get('tag_name'),
                    'description': tag.release.get('description')
                } if hasattr(tag, 'release') and tag.release else None,
                'protected': getattr(tag, 'protected', False)
            } for tag in tags
        ]
    
    # Repository Files API
    def get_default_branch(self, project_id: str) -> str:
        """Get the default branch for a project"""
        project = self.gl.projects.get(project_id)
        return getattr(project, 'default_branch', 'main')

    @retry_on_error()
    def get_file_content(self, project_id: str, file_path: str, ref: str = None) -> Dict[str, Any]:
        """Get the content of a file from the repository"""
        project = self.gl.projects.get(project_id)
        
        # Use default branch if no ref specified
        if ref is None:
            ref = self.get_default_branch(project_id)
        
        try:
            file_info = project.files.get(file_path=file_path, ref=ref)
            
            # Decode content from base64
            import base64
            content = base64.b64decode(file_info.content).decode('utf-8')
            
            return {
                'file_path': file_path,
                'content': content,
                'size': file_info.size,
                'encoding': file_info.encoding,
                'ref': ref,
                'last_commit_id': file_info.last_commit_id,
                'blob_id': file_info.blob_id
            }
        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                raise ValueError(f"File '{file_path}' not found at ref '{ref}'")
            raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise RuntimeError(f"Could not read file {file_path} at ref {ref}: {str(e)}")
    
    @retry_on_error()
    def get_repository_tree(self, project_id: str, path: str = "", ref: str = None, 
                           recursive: bool = False) -> List[Dict[str, Any]]:
        """Get repository tree (files and directories)"""
        project = self.gl.projects.get(project_id)
        
        # Use default branch if no ref specified
        if ref is None:
            ref = self.get_default_branch(project_id)
        
        kwargs = {
            'ref': ref,
            'get_all': False,
            'per_page': 100
        }
        if path:
            kwargs['path'] = path
        if recursive:
            kwargs['recursive'] = True
        
        tree_items = project.repository_tree(**kwargs)
        
        return [{
            'id': item.get('id'),
            'name': item.get('name'),
            'type': item.get('type'),  # 'tree' for dir, 'blob' for file
            'path': item.get('path'),
            'mode': item.get('mode')
        } for item in tree_items]
    
    # Commits API
    @retry_on_error()
    def get_commits(self, project_id: str, ref_name: str = None, 
                   since: Optional[str] = None, until: Optional[str] = None,
                   path: Optional[str] = None, per_page: int = DEFAULT_PAGE_SIZE, 
                   page: int = 1) -> Dict[str, Any]:
        """Get commit history for a project"""
        project = self.gl.projects.get(project_id)
        
        # Use default branch if no ref specified
        if ref_name is None:
            ref_name = self.get_default_branch(project_id)
        
        kwargs = {
            'ref_name': ref_name,
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),
            'page': page
        }
        if since:
            kwargs['since'] = since
        if until:
            kwargs['until'] = until  
        if path:
            kwargs['path'] = path
            
        commits_response = project.commits.list(**kwargs)
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(commits_response.total) if hasattr(commits_response, 'total') and commits_response.total is not None else None,
            'total_pages': int(commits_response.total_pages) if hasattr(commits_response, 'total_pages') and commits_response.total_pages is not None else None,
            'next_page': int(commits_response.next_page) if hasattr(commits_response, 'next_page') and commits_response.next_page is not None else None,
            'prev_page': int(commits_response.prev_page) if hasattr(commits_response, 'prev_page') and commits_response.prev_page is not None else None
        }
        
        return {
            'commits': [self._commit_to_dict(commit) for commit in commits_response],
            'pagination': pagination_info,
            'project_id': project_id,
            'ref': ref_name
        }
    
    @timed_cache(seconds=CACHE_TTL_LONG)
    @retry_on_error()
    def get_commit(self, project_id: str, commit_sha: str, include_stats: bool = False) -> Dict[str, Any]:
        """Get details of a specific commit"""
        project = self.gl.projects.get(project_id)
        commit = project.commits.get(commit_sha, lazy=False)
        
        result = self._commit_to_dict(commit)
        
        if include_stats:
            result['stats'] = {
                'additions': commit.stats.get('additions', 0),
                'deletions': commit.stats.get('deletions', 0), 
                'total': commit.stats.get('total', 0)
            }
            
        return result
    
    @timed_cache(seconds=CACHE_TTL_LONG)
    @retry_on_error()
    def get_commit_diff(self, project_id: str, commit_sha: str) -> List[Dict[str, Any]]:
        """Get the diff for a commit"""
        project = self.gl.projects.get(project_id)
        commit = project.commits.get(commit_sha, lazy=False)
        
        diffs = commit.diff()
        return [{
            'old_path': diff.get('old_path'),
            'new_path': diff.get('new_path'),
            'a_mode': diff.get('a_mode'),
            'b_mode': diff.get('b_mode'),
            'new_file': diff.get('new_file', False),
            'renamed_file': diff.get('renamed_file', False),
            'deleted_file': diff.get('deleted_file', False),
            'diff': diff.get('diff', '')
        } for diff in diffs]
    
    def create_commit(self, project_id: str, branch: str, commit_message: str,
                     actions: List[Dict[str, Any]], author_email: Optional[str] = None,
                     author_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a commit with multiple file changes
        
        Args:
            project_id: Project ID or path
            branch: Branch to commit to
            commit_message: Commit message
            actions: List of file actions, each with:
                - action: 'create', 'update', 'delete', 'move'
                - file_path: Path to the file
                - content: File content (for create/update)
                - previous_path: Previous path (for move)
                - encoding: 'text' or 'base64' (optional, defaults to 'text')
            author_email: Author email (optional)
            author_name: Author name (optional)
        """
        project = self.gl.projects.get(project_id)
        
        commit_data = {
            'branch': branch,
            'commit_message': commit_message,
            'actions': actions
        }
        
        if author_email:
            commit_data['author_email'] = author_email
        if author_name:
            commit_data['author_name'] = author_name
            
        commit = project.commits.create(commit_data)
        return self._commit_to_dict(commit)
    
    @retry_on_error()
    def compare_refs(self, project_id: str, from_ref: str, to_ref: str,
                    straight: bool = False) -> Dict[str, Any]:
        """Compare two refs (branches, tags, or commits)
        
        Args:
            project_id: Project ID or path
            from_ref: Source ref
            to_ref: Target ref  
            straight: If True, uses straight comparison instead of merge-base
        """
        project = self.gl.projects.get(project_id)
        comparison = project.repository_compare(from_ref, to_ref, straight=straight)
        
        return {
            'commits': [self._commit_to_dict(c) for c in comparison.get('commits', [])],
            'diffs': [{
                'old_path': diff.get('old_path'),
                'new_path': diff.get('new_path'),
                'a_mode': diff.get('a_mode'),
                'b_mode': diff.get('b_mode'),
                'new_file': diff.get('new_file', False),
                'renamed_file': diff.get('renamed_file', False),
                'deleted_file': diff.get('deleted_file', False),
                'diff': diff.get('diff', '')
            } for diff in comparison.get('diffs', [])],
            'compare_timeout': comparison.get('compare_timeout', False),
            'compare_same_ref': comparison.get('compare_same_ref', False),
            'web_url': comparison.get('web_url', '')
        }
    
    # Individual Items API
    @timed_cache(seconds=CACHE_TTL_MEDIUM)
    @retry_on_error()
    def get_issue(self, project_id: str, issue_iid: int) -> Dict[str, Any]:
        """Get a single issue by IID"""
        project = self.gl.projects.get(project_id)
        issue = project.issues.get(issue_iid, lazy=False)
        return self._issue_to_dict(issue)
    
    @timed_cache(seconds=CACHE_TTL_MEDIUM)
    @retry_on_error()
    def get_merge_request(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Get a single merge request by IID"""
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid, lazy=False)
        return self._mr_to_dict(mr)
    
    # Search API
    @retry_on_error()
    def search_projects(self, search: str, per_page: int = DEFAULT_PAGE_SIZE, 
                       page: int = 1) -> Dict[str, Any]:
        """Search for projects globally"""
        kwargs = {
            'search': search,
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),
            'page': page
        }
        
        projects_response = self.gl.projects.list(**kwargs)
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(projects_response.total) if hasattr(projects_response, 'total') and projects_response.total is not None else None,
            'total_pages': int(projects_response.total_pages) if hasattr(projects_response, 'total_pages') and projects_response.total_pages is not None else None,
            'next_page': int(projects_response.next_page) if hasattr(projects_response, 'next_page') and projects_response.next_page is not None else None,
            'prev_page': int(projects_response.prev_page) if hasattr(projects_response, 'prev_page') and projects_response.prev_page is not None else None
        }
        
        return {
            'projects': [self._project_to_dict(p) for p in projects_response],
            'pagination': pagination_info,
            'search_term': search
        }
    
    def _release_to_dict(self, release) -> Dict[str, Any]:
        """Convert a GitLab release object to a dictionary"""
        return {
            'tag_name': release.tag_name,
            'name': getattr(release, 'name', release.tag_name),
            'description': getattr(release, 'description', ''),
            'created_at': release.created_at,
            'released_at': getattr(release, 'released_at', release.created_at),
            'author': self._extract_author_info(release),
            'commit': self._extract_commit_info(release),
            'assets': self._extract_assets_info(release),
            '_links': {
                'self': getattr(release, 'web_url', ''),
                'edit_url': getattr(release, 'edit_url', '') if hasattr(release, 'edit_url') else None
            }
        }
    
    def _extract_author_info(self, release) -> Optional[Dict[str, Any]]:
        """Extract author information from release"""
        if not hasattr(release, 'author'):
            return None
        return {
            'id': release.author.get('id'),
            'username': release.author.get('username'),
            'name': release.author.get('name'),
            'avatar_url': release.author.get('avatar_url')
        }
    
    def _extract_commit_info(self, release) -> Optional[Dict[str, Any]]:
        """Extract commit information from release"""
        if not hasattr(release, 'commit'):
            return None
        return {
            'id': release.commit.get('id'),
            'short_id': release.commit.get('short_id'),
            'title': release.commit.get('title')
        }
    
    def _extract_assets_info(self, release) -> Dict[str, Any]:
        """Extract assets information from release"""
        if not hasattr(release, 'assets'):
            return {'count': 0, 'sources': [], 'links': []}
        
        assets = release.assets
        return {
            'count': getattr(assets, 'count', 0),
            'sources': [
                {
                    'format': source.get('format'),
                    'url': source.get('url')
                } for source in getattr(assets, 'sources', [])
            ],
            'links': [
                {
                    'id': link.get('id'),
                    'name': link.get('name'),
                    'url': link.get('url'),
                    'link_type': link.get('link_type')
                } for link in getattr(assets, 'links', [])
            ]
        }
    
    @retry_on_error()
    def list_releases(self, project_id: str, order_by: str = 'released_at',
                     sort: str = 'desc', per_page: int = DEFAULT_PAGE_SIZE,
                     page: int = 1) -> Dict[str, Any]:
        """List project releases"""
        project = self.gl.projects.get(project_id)
        
        kwargs = {
            'order_by': order_by,
            'sort': sort,
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),
            'page': page
        }
        
        releases_response = project.releases.list(**kwargs)
        
        releases = [self._release_to_dict(release) for release in releases_response]
        
        # Extract pagination info
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(releases_response.total) if hasattr(releases_response, 'total') and releases_response.total is not None else None,
            'total_pages': int(releases_response.total_pages) if hasattr(releases_response, 'total_pages') and releases_response.total_pages is not None else None,
            'next_page': int(releases_response.next_page) if hasattr(releases_response, 'next_page') and releases_response.next_page is not None else None,
            'prev_page': int(releases_response.prev_page) if hasattr(releases_response, 'prev_page') and releases_response.prev_page is not None else None
        }
        
        return {
            'releases': releases,
            'pagination': pagination_info
        }
    
    @retry_on_error()
    def search_in_project(self, project_id: str, scope: str, search: str,
                         per_page: int = DEFAULT_PAGE_SIZE, page: int = 1) -> Dict[str, Any]:
        """Search within a specific project
        
        scope can be: 'issues', 'merge_requests', 'milestones', 'notes', 'wiki_blobs', 'commits', 'blobs'
        """
        project = self.gl.projects.get(project_id)
        
        search_results = project.search(scope=scope, search=search, 
                                      per_page=min(per_page, MAX_PAGE_SIZE), page=page)
        
        return {
            'results': search_results,
            'scope': scope,
            'search_term': search,
            'project_id': project_id,
            'count': len(search_results)
        }
    
    @retry_on_error()
    def get_merge_request_notes(self, project_id: str, mr_iid: int, 
                               per_page: int = SMALL_PAGE_SIZE, page: int = 1,
                               sort: str = 'asc', order_by: str = 'created_at',
                               max_body_length: int = DEFAULT_MAX_BODY_LENGTH) -> Dict[str, Any]:
        """Get notes (comments) for a merge request with pagination
        
        Args:
            project_id: Project ID or path
            mr_iid: Merge request internal ID
            per_page: Number of results per page (default: 20, max: 100)
            page: Page number (default: 1)
            sort: Sort order ('asc' or 'desc', default: 'asc')
            order_by: Field to order by ('created_at' or 'updated_at', default: 'created_at')
            max_body_length: Maximum length for note bodies (0 = no limit, default: 500)
            
        Returns:
            Dictionary with notes and pagination info
        """
        project = self.gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_iid)
        
        # Prepare parameters for the notes API
        kwargs = {
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),  # GitLab max is 100
            'page': page,
            'sort': sort,
            'order_by': order_by
        }
        
        # Get notes with pagination
        notes_response = mr.notes.list(**kwargs)
        
        # Extract pagination headers
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(notes_response.total) if hasattr(notes_response, 'total') and notes_response.total is not None else None,
            'total_pages': int(notes_response.total_pages) if hasattr(notes_response, 'total_pages') and notes_response.total_pages is not None else None,
            'next_page': int(notes_response.next_page) if hasattr(notes_response, 'next_page') and notes_response.next_page is not None else None,
            'prev_page': int(notes_response.prev_page) if hasattr(notes_response, 'prev_page') and notes_response.prev_page is not None else None
        }
        
        # Process notes with optional body truncation
        processed_notes = []
        for note in notes_response:
            note_dict = self._note_to_dict(note)
            
            # Truncate body if needed
            if max_body_length > 0 and len(note_dict['body']) > max_body_length:
                note_dict['body'] = note_dict['body'][:max_body_length] + '... [truncated]'
                note_dict['truncated'] = True
            
            processed_notes.append(note_dict)
        
        return {
            'notes': processed_notes,
            'pagination': pagination_info,
            'merge_request': {
                'project_id': project_id,
                'iid': mr_iid,
                'title': mr.title,
                'web_url': mr.web_url
            }
        }
    
    @timed_cache(seconds=CACHE_TTL_LONG)
    @retry_on_error()
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get user details by username"""
        try:
            users = self.gl.users.list(username=username, get_all=False)
            if not users:
                raise ValueError(f"User '{username}' not found")
            user = users[0]
        except gitlab.exceptions.GitlabListError as e:
            logger.error(f"Error searching for user {username}: {e}")
            raise ValueError(f"Failed to search for user '{username}'")
        except ValueError:
            raise  # Re-raise our own ValueError
        except Exception as e:
            logger.error(f"Unexpected error searching for user {username}: {e}")
            raise
        return {
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'state': user.state,
            'avatar_url': user.avatar_url,
            'web_url': user.web_url
        }
    
    @retry_on_error()
    def get_user_events(self, username: str, action: Optional[str] = None, 
                       target_type: Optional[str] = None, per_page: int = DEFAULT_PAGE_SIZE,
                       page: int = 1, after: Optional[str] = None, 
                       before: Optional[str] = None) -> Dict[str, Any]:
        """Get events for a user by username with pagination
        
        Args:
            username: GitLab username
            action: Filter by action (e.g., 'commented', 'pushed', 'created', 'closed')
            target_type: Filter by target type (e.g., 'Note', 'Issue', 'MergeRequest')
            per_page: Number of results per page (default: 50, max: 100)
            page: Page number (default: 1)
            after: Date string (ISO 8601) to get events after this date
            before: Date string (ISO 8601) to get events before this date
        
        Returns:
            Dictionary with events and pagination info
        """
        # First get the user ID from username
        user = self.get_user_by_username(username)
        user_id = user['id']
        
        # Prepare parameters for the events API
        kwargs = {
            'get_all': False,
            'per_page': min(per_page, MAX_PAGE_SIZE),  # GitLab max is 100
            'page': page
        }
        
        if action:
            kwargs['action'] = action
        if target_type:
            kwargs['target_type'] = target_type
        if after:
            kwargs['after'] = after
        if before:
            kwargs['before'] = before
        
        # Get user events
        user_obj = self.gl.users.get(user_id)
        events_response = user_obj.events.list(**kwargs)
        
        # Extract pagination headers
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': int(events_response.total) if hasattr(events_response, 'total') and events_response.total is not None else None,
            'total_pages': int(events_response.total_pages) if hasattr(events_response, 'total_pages') and events_response.total_pages is not None else None,
            'next_page': int(events_response.next_page) if hasattr(events_response, 'next_page') and events_response.next_page is not None else None,
            'prev_page': int(events_response.prev_page) if hasattr(events_response, 'prev_page') and events_response.prev_page is not None else None
        }
        
        return {
            'events': [self._event_to_dict(event) for event in events_response],
            'pagination': pagination_info,
            'user': user
        }
    
    def _access_level_to_string(self, level: int) -> str:
        """Convert access level number to human-readable string"""
        access_levels = {
            10: 'Guest',
            20: 'Reporter',
            30: 'Developer',
            40: 'Maintainer',
            50: 'Owner'
        }
        return access_levels.get(level, f'Unknown ({level})')
    
    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        return {
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'path_with_namespace': project.path_with_namespace,
            'description': project.description,
            'web_url': project.web_url,
            'default_branch': getattr(project, 'default_branch', None),
            'visibility': project.visibility,
            'last_activity_at': project.last_activity_at
        }
    
    def _issue_to_dict(self, issue: Issue) -> Dict[str, Any]:
        return {
            'id': issue.id,
            'iid': issue.iid,
            'title': issue.title,
            'description': issue.description,
            'state': issue.state,
            'created_at': issue.created_at,
            'updated_at': issue.updated_at,
            'labels': issue.labels,
            'web_url': issue.web_url,
            'author': {
                'username': issue.author.get('username', 'Unknown'),
                'name': issue.author.get('name', 'Unknown')
            }
        }
    
    def _mr_to_dict(self, mr: MergeRequest) -> Dict[str, Any]:
        return {
            'id': mr.id,
            'iid': mr.iid,
            'title': mr.title,
            'description': mr.description,
            'state': mr.state,
            'source_branch': mr.source_branch,
            'target_branch': mr.target_branch,
            'created_at': mr.created_at,
            'updated_at': mr.updated_at,
            'web_url': mr.web_url,
            'author': {
                'username': mr.author.get('username', 'Unknown'),
                'name': mr.author.get('name', 'Unknown')
            }
        }
    
    def _pipeline_to_dict(self, pipeline) -> Dict[str, Any]:
        return {
            'id': pipeline.id,
            'status': pipeline.status,
            'ref': pipeline.ref,
            'sha': pipeline.sha,
            'created_at': pipeline.created_at,
            'updated_at': pipeline.updated_at,
            'web_url': pipeline.web_url
        }
    
    def _branch_to_dict(self, branch) -> Dict[str, Any]:
        return {
            'name': branch.name,
            'merged': branch.merged,
            'protected': branch.protected,
            'default': branch.default,
            'web_url': branch.web_url
        }
    
    def _commit_to_dict(self, commit) -> Dict[str, Any]:
        return {
            'id': commit.id,
            'short_id': commit.short_id,
            'title': commit.title,
            'message': commit.message,
            'author_name': commit.author_name,
            'author_email': commit.author_email,
            'authored_date': commit.authored_date,
            'committer_name': commit.committer_name,
            'committer_email': commit.committer_email,
            'committed_date': commit.committed_date,
            'created_at': commit.created_at,
            'parent_ids': getattr(commit, 'parent_ids', []),
            'web_url': commit.web_url if hasattr(commit, 'web_url') else None
        }
    
    def _note_to_dict(self, note) -> Dict[str, Any]:
        return {
            'id': note.id,
            'body': note.body,
            'created_at': note.created_at,
            'updated_at': note.updated_at,
            'author': {
                'username': note.author.get('username', 'Unknown'),
                'name': note.author.get('name', 'Unknown')
            },
            'system': getattr(note, 'system', False),
            'noteable_type': note.noteable_type,
            'noteable_iid': note.noteable_iid,
            'resolvable': getattr(note, 'resolvable', False),
            'resolved': getattr(note, 'resolved', False)
        }
    
    def _event_to_dict(self, event) -> Dict[str, Any]:
        """Convert GitLab event object to dictionary"""
        event_dict = {
            'id': event.id,
            'title': getattr(event, 'title', None),
            'project_id': getattr(event, 'project_id', None),
            'action_name': event.action_name,
            'target_id': getattr(event, 'target_id', None),
            'target_type': getattr(event, 'target_type', None),
            'target_title': getattr(event, 'target_title', None),
            'created_at': event.created_at,
            'author': {
                'id': event.author_id,
                'username': event.author_username,
                'name': event.author.get('name', '') if hasattr(event, 'author') and event.author else '',
                'state': event.author.get('state', '') if hasattr(event, 'author') and event.author else '',
                'avatar_url': event.author.get('avatar_url', '') if hasattr(event, 'author') and event.author else '',
                'web_url': event.author.get('web_url', '') if hasattr(event, 'author') and event.author else ''
            }
        }
        
        # Add push data if available
        if hasattr(event, 'push_data') and event.push_data:
            event_dict['push_data'] = {
                'action': event.push_data.get('action'),
                'ref_type': event.push_data.get('ref_type'),
                'commit_count': event.push_data.get('commit_count'),
                'ref': event.push_data.get('ref'),
                'commit_title': event.push_data.get('commit_title')
            }
        
        # Add note/comment details if this is a comment event
        if hasattr(event, 'note') and event.note:
            event_dict['note'] = {
                'id': event.note.get('id'),
                'body': event.note.get('body'),
                'noteable_type': event.note.get('noteable_type'),
                'noteable_id': event.note.get('noteable_id')
            }
        
        # Add wiki page info if available
        if hasattr(event, 'wiki_page') and event.wiki_page:
            event_dict['wiki_page'] = {
                'title': event.wiki_page.get('title'),
                'action': event.wiki_page.get('action')
            }
        
        return event_dict
    
    # AI Helper Methods
    def summarize_merge_request(self, project_id: str, mr_iid: int, max_length: int = 500) -> Dict[str, Any]:
        """Generate a summary of a merge request for AI consumption"""
        mr_data = self.get_merge_request(project_id, mr_iid)
        changes = self.get_merge_request_changes(project_id, mr_iid)
        
        # Get first few discussions
        discussions = self.get_merge_request_discussions(project_id, mr_iid, per_page=5)
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"MR !{mr_data['iid']}: {mr_data['title']}")
        summary_parts.append(f"Author: @{mr_data['author']['username']}")
        summary_parts.append(f"Branch: {mr_data['source_branch']} → {mr_data['target_branch']}")
        summary_parts.append(f"State: {mr_data['state']}")
        
        # Changes summary
        total_changes = len(changes['changes'])
        files_added = sum(1 for c in changes['changes'] if c['new_file'])
        files_modified = sum(1 for c in changes['changes'] if not c['new_file'] and not c['deleted_file'])
        files_deleted = sum(1 for c in changes['changes'] if c['deleted_file'])
        
        summary_parts.append(f"\nChanges: {total_changes} files ({files_added} added, {files_modified} modified, {files_deleted} deleted)")
        
        # Description snippet
        if mr_data.get('description'):
            desc_snippet = mr_data['description'][:200]
            if len(mr_data['description']) > 200:
                desc_snippet += "..."
            summary_parts.append(f"\nDescription: {desc_snippet}")
        
        # Discussion summary
        total_discussions = discussions['pagination']['total'] or len(discussions['discussions'])
        unresolved = sum(1 for d in discussions['discussions'] 
                        for n in d['notes'] 
                        if n.get('resolvable') and not n.get('resolved'))
        
        summary_parts.append(f"\nDiscussions: {total_discussions} threads ({unresolved} unresolved)")
        
        # Pipeline status
        if mr_data.get('pipeline'):
            summary_parts.append(f"Pipeline: {mr_data['pipeline']['status']}")
        
        summary = "\n".join(summary_parts)
        
        # Truncate if needed
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return {
            'merge_request_iid': mr_iid,
            'summary': summary,
            'stats': {
                'files_changed': total_changes,
                'files_added': files_added,
                'files_modified': files_modified,
                'files_deleted': files_deleted,
                'discussions': total_discussions,
                'unresolved_threads': unresolved
            }
        }
    
    def summarize_issue(self, project_id: str, issue_iid: int, max_length: int = 500) -> Dict[str, Any]:
        """Generate a summary of an issue for AI consumption"""
        issue = self.get_issue(project_id, issue_iid)
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Issue #{issue['iid']}: {issue['title']}")
        summary_parts.append(f"Author: @{issue['author']['username']}")
        summary_parts.append(f"State: {issue['state']}")
        summary_parts.append(f"Created: {issue['created_at']}")
        
        # Labels
        if issue.get('labels'):
            summary_parts.append(f"Labels: {', '.join(issue['labels'])}")
        
        # Assignees
        if issue.get('assignees'):
            assignees = ', '.join(f"@{a['username']}" for a in issue['assignees'])
            summary_parts.append(f"Assignees: {assignees}")
        
        # Description snippet
        if issue.get('description'):
            desc_snippet = issue['description'][:200]
            if len(issue['description']) > 200:
                desc_snippet += "..."
            summary_parts.append(f"\nDescription: {desc_snippet}")
        
        # Due date
        if issue.get('due_date'):
            summary_parts.append(f"Due: {issue['due_date']}")
        
        # Weight/time tracking
        if issue.get('time_stats'):
            time_stats = issue['time_stats']
            if time_stats.get('time_estimate'):
                summary_parts.append(f"Estimate: {time_stats['human_time_estimate']}")
            if time_stats.get('total_time_spent'):
                summary_parts.append(f"Spent: {time_stats['human_total_time_spent']}")
        
        summary = "\n".join(summary_parts)
        
        # Truncate if needed
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return {
            'issue_iid': issue_iid,
            'summary': summary,
            'metadata': {
                'state': issue['state'],
                'labels': issue.get('labels', []),
                'has_assignees': bool(issue.get('assignees')),
                'has_due_date': bool(issue.get('due_date')),
                'has_time_tracking': bool(issue.get('time_stats', {}).get('time_estimate'))
            }
        }
    
    def summarize_pipeline(self, project_id: str, pipeline_id: int, max_length: int = 500) -> Dict[str, Any]:
        """Generate a summary of a pipeline for AI consumption"""
        project = self.gl.projects.get(project_id)
        pipeline = project.pipelines.get(pipeline_id)
        
        # Get jobs for the pipeline
        jobs = pipeline.jobs.list(get_all=False, per_page=20)
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Pipeline #{pipeline.id}")
        summary_parts.append(f"Status: {pipeline.status}")
        summary_parts.append(f"Ref: {pipeline.ref}")
        summary_parts.append(f"SHA: {pipeline.sha[:8]}")
        summary_parts.append(f"Created: {pipeline.created_at}")
        
        # Duration
        if hasattr(pipeline, 'duration') and pipeline.duration:
            summary_parts.append(f"Duration: {pipeline.duration}s")
        
        # Jobs summary
        job_statuses = {}
        for job in jobs:
            status = job.status
            job_statuses[status] = job_statuses.get(status, 0) + 1
        
        job_summary = ", ".join(f"{count} {status}" for status, count in job_statuses.items())
        summary_parts.append(f"\nJobs: {job_summary}")
        
        # Failed jobs details
        failed_jobs = [j for j in jobs if j.status == 'failed']
        if failed_jobs:
            summary_parts.append("\nFailed jobs:")
            for job in failed_jobs[:3]:  # Show max 3 failed jobs
                summary_parts.append(f"- {job.name} (stage: {job.stage})")
        
        # Trigger info
        if hasattr(pipeline, 'user') and pipeline.user:
            summary_parts.append(f"\nTriggered by: @{pipeline.user['username']}")
        
        summary = "\n".join(summary_parts)
        
        # Truncate if needed
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return {
            'pipeline_id': pipeline_id,
            'summary': summary,
            'stats': {
                'status': pipeline.status,
                'total_jobs': len(jobs),
                'job_statuses': job_statuses,
                'failed_count': len(failed_jobs),
                'duration': getattr(pipeline, 'duration', None)
            }
        }
    
    def _parse_diff_hunks(self, diff_content: str) -> tuple[List[Dict[str, Any]], int, int]:
        """Parse diff content into hunks and count additions/deletions"""
        hunks = []
        current_hunk = None
        total_additions = 0
        total_deletions = 0
        
        for line in diff_content.split('\n'):
            if line.startswith('@@'):
                # New hunk
                if current_hunk:
                    hunks.append(current_hunk)
                current_hunk = {
                    'header': line,
                    'lines': [],
                    'additions': 0,
                    'deletions': 0
                }
            elif current_hunk:
                current_hunk['lines'].append(line)
                if line.startswith('+') and not line.startswith('+++'):
                    current_hunk['additions'] += 1
                    total_additions += 1
                elif line.startswith('-') and not line.startswith('---'):
                    current_hunk['deletions'] += 1
                    total_deletions += 1
        
        if current_hunk:
            hunks.append(current_hunk)
            
        return hunks, total_additions, total_deletions
    
    def _process_single_diff(self, diff: Dict[str, Any], max_file_size: int) -> tuple[Dict[str, Any], int, int, bool]:
        """Process a single diff entry"""
        diff_content = diff.get('diff', '')
        file_path = diff['new_path'] or diff['old_path']
        truncated = False
        
        # Check if diff is too large
        if len(diff_content) > max_file_size:
            truncated = True
            diff_content = diff_content[:max_file_size] + "\n... [diff truncated]"
        
        # Parse diff to extract hunks
        hunks, additions, deletions = self._parse_diff_hunks(diff_content)
        
        return {
            'file_path': file_path,
            'old_path': diff['old_path'],
            'new_path': diff['new_path'],
            'file_mode_changed': diff['a_mode'] != diff['b_mode'],
            'new_file': diff['new_file'],
            'deleted_file': diff['deleted_file'],
            'renamed_file': diff['renamed_file'],
            'hunks': hunks,
            'additions': sum(h['additions'] for h in hunks),
            'deletions': sum(h['deletions'] for h in hunks),
            'truncated': truncated
        }, additions, deletions, truncated
    
    # Advanced Diff Tools
    def smart_diff(self, project_id: str, from_ref: str, to_ref: str, 
                  context_lines: int = 3, max_file_size: int = 50000) -> Dict[str, Any]:
        """Get a structured diff between two refs with size limits
        
        Args:
            project_id: Project ID or path
            from_ref: Source ref (branch, tag, or commit)
            to_ref: Target ref
            context_lines: Number of context lines around changes
            max_file_size: Maximum diff size per file in characters
        """
        # Note: context_lines parameter is reserved for future use when implementing
        # custom diff generation. Currently using GitLab's default context.
        comparison = self.compare_refs(project_id, from_ref, to_ref)
        
        structured_diffs = []
        total_additions = 0
        total_deletions = 0
        truncated_files = []
        
        for diff in comparison['diffs']:
            structured_diff, additions, deletions, truncated = self._process_single_diff(diff, max_file_size)
            structured_diffs.append(structured_diff)
            total_additions += additions
            total_deletions += deletions
            if truncated:
                truncated_files.append(structured_diff['file_path'])
        
        return {
            'from_ref': from_ref,
            'to_ref': to_ref,
            'commits_count': len(comparison['commits']),
            'files_changed': len(structured_diffs),
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'diffs': structured_diffs,
            'truncated_files': truncated_files,
            'compare_timeout': comparison.get('compare_timeout', False),
            'web_url': comparison.get('web_url', '')
        }
    
    def safe_preview_commit(self, project_id: str, branch: str, 
                           commit_message: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preview what a commit would look like without actually creating it
        
        Args:
            project_id: Project ID or path
            branch: Branch to preview commit on
            commit_message: Commit message
            actions: List of file actions (same format as create_commit)
        
        Returns:
            Preview of the commit including diffs
        """
        project = self.gl.projects.get(project_id)
        
        # Get current branch state
        branch_info = project.branches.get(branch)
        current_commit = branch_info.commit['id']
        
        preview = {
            'branch': branch,
            'base_commit': current_commit,
            'commit_message': commit_message,
            'actions': [],
            'estimated_changes': {
                'files_added': 0,
                'files_modified': 0,
                'files_deleted': 0,
                'files_moved': 0
            }
        }
        
        for action in actions:
            action_type = action.get('action')
            file_path = action.get('file_path')
            
            action_preview = {
                'action': action_type,
                'file_path': file_path,
                'valid': True,
                'issues': []
            }
            
            if action_type == 'create':
                # Check if file already exists
                try:
                    project.files.get(file_path=file_path, ref=branch)
                    action_preview['issues'].append(f"File already exists: {file_path}")
                    action_preview['valid'] = False
                except gitlab.exceptions.GitlabGetError:
                    preview['estimated_changes']['files_added'] += 1
                    
            elif action_type == 'update':
                # Check if file exists
                try:
                    project.files.get(file_path=file_path, ref=branch)
                    preview['estimated_changes']['files_modified'] += 1
                except gitlab.exceptions.GitlabGetError:
                    action_preview['issues'].append(f"File not found: {file_path}")
                    action_preview['valid'] = False
                    
            elif action_type == 'delete':
                # Check if file exists
                try:
                    project.files.get(file_path=file_path, ref=branch)
                    preview['estimated_changes']['files_deleted'] += 1
                except gitlab.exceptions.GitlabGetError:
                    action_preview['issues'].append(f"File not found: {file_path}")
                    action_preview['valid'] = False
                    
            elif action_type == 'move':
                previous_path = action.get('previous_path')
                if not previous_path:
                    action_preview['issues'].append("Move action requires 'previous_path'")
                    action_preview['valid'] = False
                else:
                    # Check if source exists and destination doesn't
                    try:
                        project.files.get(file_path=previous_path, ref=branch)
                        try:
                            project.files.get(file_path=file_path, ref=branch)
                            action_preview['issues'].append(f"Destination already exists: {file_path}")
                            action_preview['valid'] = False
                        except gitlab.exceptions.GitlabGetError:
                            preview['estimated_changes']['files_moved'] += 1
                    except gitlab.exceptions.GitlabGetError:
                        action_preview['issues'].append(f"Source file not found: {previous_path}")
                        action_preview['valid'] = False
            
            # Add content preview for create/update
            if action_type in ['create', 'update'] and action.get('content'):
                content_preview = action['content'][:200]
                if len(action['content']) > 200:
                    content_preview += "..."
                action_preview['content_preview'] = content_preview
                action_preview['content_size'] = len(action['content'])
            
            preview['actions'].append(action_preview)
        
        # Overall validity
        preview['valid'] = all(a['valid'] for a in preview['actions'])
        preview['total_issues'] = sum(len(a['issues']) for a in preview['actions'])
        
        return preview
    
    # Batch Operations
    def batch_operations(self, project_id: str, operations: List[Dict[str, Any]], 
                        stop_on_error: bool = True) -> Dict[str, Any]:
        """Execute multiple operations atomically with rollback on failure
        
        Args:
            project_id: Project ID or path
            operations: List of operations to execute, each with:
                - tool: Tool name (e.g., 'gitlab_create_commit', 'gitlab_get_issue')
                - arguments: Arguments for the tool
                - name: Optional name for the operation (for referencing results)
            stop_on_error: If True, stop and rollback on first error
        
        Returns:
            Results of all operations with rollback information if applicable
        """
        results = {
            'success': True,
            'operations': [],
            'rollback_performed': False,
            'rollback_operations': []
        }
        
        if not operations:
            return results
        
        completed_operations = []
        operation_context = {}  # Store results that can be referenced by later operations
        
        try:
            for i, operation in enumerate(operations):
                op_tool = operation.get('tool')
                op_arguments = operation.get('arguments', {})
                op_name = operation.get('name', f'operation_{i}')
                
                # Substitute any references to previous operation results
                op_arguments = self._substitute_operation_references(op_arguments, operation_context)
                
                op_result = {
                    'name': op_name,
                    'tool': op_tool,
                    'status': 'pending',
                    'result': None,
                    'error': None
                }
                
                try:
                    # Import tool handlers to execute the operation (lazy import to avoid circular dependency)
                    from . import tool_handlers
                    
                    # Execute the operation using the tool handler
                    if op_tool in tool_handlers.TOOL_HANDLERS:
                        handler = tool_handlers.TOOL_HANDLERS[op_tool]
                        # Ensure project_id is in arguments if not already present
                        if 'project_id' not in op_arguments:
                            op_arguments['project_id'] = project_id
                        
                        # Execute the handler
                        result = handler(self, op_arguments)
                        op_result['result'] = result
                        
                        # Set up rollback based on the tool type
                        if op_tool == 'gitlab_create_commit':
                            op_result['rollback'] = {
                                'type': 'revert_commit', 
                                'commit_id': result.get('id'),
                                'branch': op_arguments.get('branch')
                            }
                        elif op_tool in ['gitlab_create_merge_request', 'gitlab_update_merge_request']:
                            if op_tool == 'gitlab_update_merge_request':
                                # Store original state for rollback
                                original = self.get_merge_request(project_id, op_arguments.get('mr_iid'))
                                op_result['rollback'] = {
                                    'type': 'update_mr',
                                    'mr_iid': op_arguments.get('mr_iid'),
                                    'original_state': original
                                }
                            else:
                                op_result['rollback'] = {'type': 'close_mr', 'mr_iid': result.get('iid')}
                        elif op_tool == 'gitlab_create_tag':
                            op_result['rollback'] = {'type': 'delete_tag', 'tag_name': result.get('name')}
                        # Most other operations don't have direct rollbacks
                        
                    else:
                        raise ValueError(f"Unknown tool: {op_tool}")
                    
                    op_result['status'] = 'success'
                    completed_operations.append(op_result)
                    
                    # Store result in context for later operations
                    operation_context[op_name] = op_result['result']
                    
                except Exception as e:
                    op_result['status'] = 'failed'
                    op_result['error'] = str(e)
                    results['success'] = False
                    
                    if stop_on_error:
                        # Perform rollback
                        results['rollback_performed'] = True
                        results['operations'].append(op_result)
                        
                        # Rollback in reverse order
                        for completed_op in reversed(completed_operations):
                            if 'rollback' in completed_op:
                                rollback_result = self._perform_rollback(
                                    project_id, 
                                    completed_op['rollback']
                                )
                                results['rollback_operations'].append(rollback_result)
                        
                        raise e
                
                results['operations'].append(op_result)
                
        except Exception as e:
            # Re-raise if stop_on_error is True
            if stop_on_error:
                raise
        
        return results
    
    def _substitute_operation_references(self, params: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute references to previous operation results
        
        References are in the format: {{operation_name.field_path}}
        """
        import re
        import json
        
        def substitute(value):
            if isinstance(value, str):
                # Find all references
                pattern = r'\{\{(\w+)\.([^\}]+)\}\}'
                matches = re.findall(pattern, value)
                
                for op_name, field_path in matches:
                    if op_name in context:
                        # Navigate the field path
                        result = context[op_name]
                        for field in field_path.split('.'):
                            if isinstance(result, dict):
                                result = result.get(field)
                            else:
                                break
                        
                        if result is not None:
                            value = value.replace(f'{{{{{op_name}.{field_path}}}}}', str(result))
                
                return value
            elif isinstance(value, dict):
                return {k: substitute(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute(v) for v in value]
            else:
                return value
        
        return substitute(params)
    
    def _perform_rollback(self, project_id: str, rollback_info: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a rollback operation"""
        rollback_type = rollback_info.get('type')
        result = {
            'type': rollback_type,
            'status': 'pending',
            'error': None
        }
        
        try:
            project = self.gl.projects.get(project_id)
            
            if rollback_type == 'delete_branch':
                branch = project.branches.get(rollback_info['branch'])
                branch.delete()
                result['status'] = 'success'
                
            elif rollback_type == 'close_mr':
                self.close_merge_request(project_id, rollback_info['mr_iid'])
                result['status'] = 'success'
                
            elif rollback_type == 'update_mr':
                # Restore original state
                original = rollback_info['original_state']
                self.update_merge_request(
                    project_id, 
                    rollback_info['mr_iid'],
                    title=original.get('title'),
                    description=original.get('description'),
                    labels=original.get('labels')
                )
                result['status'] = 'success'
                
            elif rollback_type == 'delete_tag':
                tag = project.tags.get(rollback_info['tag_name'])
                tag.delete()
                result['status'] = 'success'
                
            elif rollback_type == 'revert_commit':
                # Create a revert commit
                commit = project.commits.get(rollback_info['commit_id'])
                commit.revert(branch=rollback_info['branch'])
                result['status'] = 'success'
                
            else:
                result['status'] = 'skipped'
                result['error'] = f"Unknown rollback type: {rollback_type}"
                
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def get_project_from_git(self, path: str = ".") -> Optional[Dict[str, Any]]:
        """Get GitLab project details from a git repository
        
        Args:
            path: Path to the git repository (default: current directory)
            
        Returns:
            Project details with additional git information, or None if not found
        """
        detected = GitDetector.detect_gitlab_project(path)
        if not detected:
            return None
        
        # Check if the URL belongs to the configured GitLab instance
        if not GitDetector.is_gitlab_url(detected['url'], self.config.url):
            return None
        
        # Get the project using the path
        try:
            project = self.get_project(detected['path'])
            # Add git-specific information to the project data
            project['git_info'] = {
                'current_branch': detected.get('branch'),
                'remote_url': detected['url'],
                'detected_from': path
            }
            return project
        except Exception:
            # Project might not be accessible or doesn't exist
            return None