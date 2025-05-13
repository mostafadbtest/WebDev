
async function delete_user(user_id) {
    try {
        console.log("Deleting user", user_id);
        const response = await fetch(`/api/v1/users/${user_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            document.getElementById(`user-${user_id}`).remove();
        } else {
            console.error("Failed to delete user");
        }
    } catch (err) {
        console.error("Error:", err);
    }
}









