def return_all_implemented_tools():
    from tools.issues import (
        add_issue_comment_tool,
        create_issue_tool,
        get_issue_tool,
        list_issues_tool,
        search_issues_tool,
        update_issue_tool,
        get_issue_comments_tool,
    )

    from tools.repository_management import (
        get_file_contents_tool,
        create_branch_tool,
        create_repository_tool,
        get_file_tool,
        write_file_tool,
        delete_file_tool,
        push_files_tool,
        list_commits_tool,
        get_commit_tool,
        list_branches_tool,
        search_repositories_tool,
    )

    from tools.user import (
        list_notifications_tool,
        get_me_tool,
        search_users_tool,
    )

    return [
        list_notifications_tool,
        search_users_tool,
        list_issues_tool,
        update_issue_tool,
        add_issue_comment_tool,
        get_issue_tool,
        create_issue_tool,
        get_file_contents_tool,
        create_branch_tool,
        create_repository_tool,
        get_me_tool,
        get_file_tool,
        write_file_tool,
        delete_file_tool,
        push_files_tool,
        search_repositories_tool,
        list_commits_tool,
        get_commit_tool,
        list_branches_tool,
        search_issues_tool,
        get_issue_comments_tool,
    ]
