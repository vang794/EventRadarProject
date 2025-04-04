document.addEventListener('DOMContentLoaded', function() {
    // Get the user role from a meta tag or data attribute (depending on how it's passed from Django)
    const userRole = document.getElementById('user_role').getAttribute('data-role');
    console.log(userRole);
    // Get the buttons by their ID

    const eventAppButton = document.getElementById('event-app-btn');
    const approveButton = document.getElementById('approve-btn');

    if (eventAppButton) eventAppButton.style.display = 'none';
    if (approveButton) approveButton.style.display = 'none';

    if (userRole === 'User' || userRole === 'Admin') {
        if (eventAppButton) {
            eventAppButton.style.display = 'inline-block';}
    }
    // Check if the user role is 'Admin' or 'Event Manager'
     if (userRole === 'Admin') {
        // If user is Admin , show the buttons
        approveButton.style.display = 'inline-block';

    } if (userRole === 'Admin' || userRole === 'Event_Manager') {
        // If user is Admin or Event Manager, show the buttons
        //This is where the buttons for manage/add events would be
    }

});