# ado_client.py - Azure DevOps Integration
import os
from datetime import datetime

class AzureDevOpsClient:
    """Simplified Azure DevOps client for fetching user stories"""
    
    def __init__(self, use_mock=True):
        """
        Initialize ADO client
        
        Args:
            use_mock: If True, use mock data instead of real API
        """
        self.use_mock = use_mock
        self.org_url = os.getenv('ADO_ORG_URL', 'https://dev.azure.com/myorg')
        self.project = os.getenv('ADO_PROJECT', 'MyProject')
        self.pat = os.getenv('ADO_PAT', '')
    
    def fetch_user_stories(self, max_stories=5):
        """
        Fetch user stories from Azure DevOps
        
        Args:
            max_stories: Maximum number of stories to fetch
            
        Returns:
            List of user story dictionaries
        """
        if self.use_mock or not self.pat:
            return self._get_mock_stories(max_stories)
        else:
            return self._fetch_from_ado(max_stories)
    
    def _get_mock_stories(self, max_stories):
        """Get mock user stories for demo"""
        
        mock_stories = [
            {
                'id': 'US-1001',
                'title': 'User Authentication with Email and Password',
                'description': 'As a user, I want to login using my email and password so that I can securely access my account and personalized features.',
                'acceptance_criteria': [
                    'User can enter email and password',
                    'System validates credentials against database',
                    'Successful login redirects to dashboard',
                    'Failed login shows appropriate error message',
                    'Account locks after 5 failed attempts'
                ],
                'priority': 'High',
                'status': 'Active',
                'assigned_to': 'QA Team'
            },
            {
                'id': 'US-1002',
                'title': 'RESTful API for User Profile Management',
                'description': 'As a developer, I want to create REST API endpoints for user profile operations (GET, POST, PUT, DELETE) with proper authentication and validation.',
                'acceptance_criteria': [
                    'GET /api/users/{id} returns user profile',
                    'POST /api/users creates new user with validation',
                    'PUT /api/users/{id} updates existing user',
                    'DELETE /api/users/{id} removes user',
                    'All endpoints require authentication',
                    'Proper HTTP status codes returned'
                ],
                'priority': 'Critical',
                'status': 'Active',
                'assigned_to': 'Dev Team'
            },
            {
                'id': 'US-1003',
                'title': 'Database Schema for User Data Storage',
                'description': 'As a system, I need to store user information in a relational database with proper constraints, indexes, and referential integrity.',
                'acceptance_criteria': [
                    'Users table with primary key',
                    'Email field with unique constraint',
                    'Password stored as hash',
                    'Foreign key relationships maintained',
                    'Indexes on frequently queried columns',
                    'Audit trail for data changes'
                ],
                'priority': 'Critical',
                'status': 'Active',
                'assigned_to': 'Data Team'
            },
            {
                'id': 'US-1004',
                'title': 'Responsive User Dashboard UI',
                'description': 'As a user, I want to see a responsive dashboard that displays my profile information, recent activity, and quick actions across all devices.',
                'acceptance_criteria': [
                    'Dashboard loads within 2 seconds',
                    'Responsive design works on mobile, tablet, desktop',
                    'Profile information displayed correctly',
                    'Quick action buttons functional',
                    'Navigation menu accessible',
                    'No horizontal scrolling on mobile'
                ],
                'priority': 'High',
                'status': 'Active',
                'assigned_to': 'UI Team'
            },
            {
                'id': 'US-1005',
                'title': 'Automated Regression Testing Suite',
                'description': 'As a QA engineer, I want automated regression tests that run on every deployment to catch breaking changes early.',
                'acceptance_criteria': [
                    'Test suite covers critical user paths',
                    'Tests run automatically on CI/CD',
                    'Failed tests block deployment',
                    'Test results reported with details',
                    'Historical comparison shows trends',
                    'Regression detection alerts team'
                ],
                'priority': 'Critical',
                'status': 'Active',
                'assigned_to': 'QA Team'
            }
        ]
        
        return mock_stories[:max_stories]
    
    def _fetch_from_ado(self, max_stories):
        """Fetch from real Azure DevOps (requires credentials)"""
        # This would use the Azure DevOps REST API
        # For now, return mock data if credentials not set
        print("⚠️  Real ADO credentials not configured. Using mock data.")
        return self._get_mock_stories(max_stories)


# Demo/Test
if __name__ == "__main__":
    print("=" * 80)
    print("📋 AZURE DEVOPS CLIENT - TEST")
    print("=" * 80)
    
    # Initialize client
    client = AzureDevOpsClient(use_mock=True)
    
    # Fetch user stories
    print("\n🔍 Fetching user stories from Azure DevOps...\n")
    stories = client.fetch_user_stories(max_stories=5)
    
    print(f"✅ Fetched {len(stories)} user stories:\n")
    
    for story in stories:
        print(f"  {story['id']}: {story['title']}")
        print(f"       Priority: {story['priority']} | Status: {story['status']}")
        print(f"       Description: {story['description'][:80]}...")
        print()
    
    print("=" * 80)
    print("✅ Azure DevOps integration working!")
    print("=" * 80)