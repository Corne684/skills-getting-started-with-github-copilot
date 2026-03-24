"""
Unit tests for the Mergington High School API using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static_html(self, client):
        """
        Arrange: Set up client fixture.
        Act: Make GET request to root endpoint without following redirects.
        Assert: Verify redirect response and location header.
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """
        Arrange: Set up client fixture.
        Act: Make GET request to /activities endpoint.
        Assert: Verify successful response status.
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """
        Arrange: Set up client fixture.
        Act: Make GET request to /activities endpoint and parse JSON.
        Assert: Verify response is a dictionary.
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_contains_all_expected_activities(self, client):
        """
        Arrange: Define expected activities from the app.
        Act: Make GET request to /activities endpoint and parse JSON.
        Assert: Verify all expected activities are present.
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Band",
            "Debate Team",
            "Science Club",
        ]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self, client):
        """
        Arrange: Define required fields for each activity.
        Act: Make GET request to /activities endpoint and parse JSON.
        Assert: Verify each activity contains all required fields.
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert (
                    field in activity_data
                ), f"Missing field '{field}' in activity '{activity_name}'"

    def test_activity_participants_is_list(self, client):
        """
        Arrange: Set up client fixture.
        Act: Make GET request to /activities endpoint and parse JSON.
        Assert: Verify participants field is a list for all activities.
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(
                activity_data["participants"], list
            ), f"Participants for '{activity_name}' is not a list"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, sample_email):
        """
        Arrange: Set up client and sample email.
        Act: Make POST request to signup endpoint with valid activity and email.
        Assert: Verify successful response with confirmation message.
        """
        # Act
        response = client.post(
            "/activities/Chess Club/signup", params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_email):
        """
        Arrange: Set up client and sample email.
        Act: Make POST request to signup, then GET activities to verify state.
        Assert: Verify participant was added to the activity's participant list.
        """
        # Act: Sign up
        signup_response = client.post(
            "/activities/Art Studio/signup", params={"email": sample_email}
        )
        assert signup_response.status_code == 200

        # Act: Get activities to verify state
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        assert sample_email in activities["Art Studio"]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client, sample_email):
        """
        Arrange: Set up client and sample email.
        Act: Make POST request to signup for nonexistent activity.
        Assert: Verify 404 response with appropriate error message.
        """
        # Act
        response = client.post(
            "/activities/Nonexistent Activity/signup", params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client, sample_email):
        """
        Arrange: Sign up a student once for an activity.
        Act: Attempt to signup the same student again for the same activity.
        Assert: Verify 400 error response for duplicate signup.
        """
        # Arrange: First signup
        client.post(
            "/activities/Tennis Club/signup", params={"email": sample_email}
        )

        # Act: Try to sign up again
        response = client.post(
            "/activities/Tennis Club/signup", params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_multiple_students_can_signup_for_same_activity(self, client):
        """
        Arrange: Set up two different email addresses.
        Act: Sign up both students for the same activity.
        Assert: Verify both participants are added to the activity.
        """
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act: Sign up first student
        response1 = client.post(
            "/activities/Music Band/signup", params={"email": email1}
        )
        assert response1.status_code == 200

        # Act: Sign up second student
        response2 = client.post(
            "/activities/Music Band/signup", params={"email": email2}
        )
        assert response2.status_code == 200

        # Act: Get activities to verify state
        activities_response = client.get("/activities")
        participants = activities_response.json()["Music Band"]["participants"]

        # Assert
        assert email1 in participants
        assert email2 in participants

    def test_student_can_signup_for_different_activities(self, client, sample_email):
        """
        Arrange: Set up client and sample email.
        Act: Sign up the same student for two different activities.
        Assert: Verify student is added to both activities.
        """
        # Act: Sign up for first activity
        response1 = client.post(
            "/activities/Debate Team/signup", params={"email": sample_email}
        )
        assert response1.status_code == 200

        # Act: Sign up for second activity
        response2 = client.post(
            "/activities/Science Club/signup", params={"email": sample_email}
        )
        assert response2.status_code == 200

        # Act: Get activities to verify state
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        assert sample_email in activities["Debate Team"]["participants"]
        assert sample_email in activities["Science Club"]["participants"]


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_successful(self, client, sample_email):
        """
        Arrange: Sign up a student for an activity.
        Act: Make DELETE request to remove the student.
        Assert: Verify successful removal response.
        """
        # Arrange: Sign up
        client.post(
            "/activities/Programming Class/signup", params={"email": sample_email}
        )

        # Act
        response = client.delete(
            "/activities/Programming Class/participants",
            params={"email": sample_email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_remove_participant_removes_from_activity(self, client, sample_email):
        """
        Arrange: Sign up a student for an activity.
        Act: Remove the student, then get activities to verify state.
        Assert: Verify student is no longer in the participant list.
        """
        # Arrange: Sign up
        client.post(
            "/activities/Gym Class/signup", params={"email": sample_email}
        )

        # Act: Remove participant
        remove_response = client.delete(
            "/activities/Gym Class/participants", params={"email": sample_email}
        )
        assert remove_response.status_code == 200

        # Act: Get activities to verify state
        activities_response = client.get("/activities")
        participants = activities_response.json()["Gym Class"]["participants"]

        # Assert
        assert sample_email not in participants

    def test_remove_from_nonexistent_activity_returns_404(self, client, sample_email):
        """
        Arrange: Set up client and sample email.
        Act: Make DELETE request for nonexistent activity.
        Assert: Verify 404 response.
        """
        # Act
        response = client.delete(
            "/activities/Nonexistent Activity/participants",
            params={"email": sample_email},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client, sample_email):
        """
        Arrange: Set up client and sample email for a student not signed up.
        Act: Make DELETE request to remove a nonexistent participant.
        Assert: Verify 404 response with appropriate error message.
        """
        # Act
        response = client.delete(
            "/activities/Basketball Team/participants", params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_one_participant_doesnt_affect_others(self, client):
        """
        Arrange: Sign up two students for the same activity.
        Act: Remove one student.
        Assert: Verify the other student remains in the participant list.
        """
        # Arrange
        email1 = "persistent.student@mergington.edu"
        email2 = "removed.student@mergington.edu"

        # Arrange: Sign up both students
        client.post("/activities/Chess Club/signup", params={"email": email1})
        client.post("/activities/Chess Club/signup", params={"email": email2})

        # Act: Remove only the second student
        remove_response = client.delete(
            "/activities/Chess Club/participants", params={"email": email2}
        )
        assert remove_response.status_code == 200

        # Act: Get activities to verify state
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]

        # Assert
        assert email1 in participants
        assert email2 not in participants
