function goToProfile() {
    window.location.href = "/profile?user_id=" + userId;
}

function openSubscriptionsAdmin() {
    window.location.href = "/admin-subscriptions?user_id=" + userId;
}

function editUser(userUniqueId) {
    window.location.href = "/admin-edit-user/" + userUniqueId + "?user_id=" + userId;
}