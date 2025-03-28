function confirmAction() {
    // If the user confirms, hide the confirmation overlay and show the form
    document.getElementById('confirmation-overlay').style.display = 'none';
    document.getElementById('content').style.display = 'block';
}

function cancelAction() {
    // Go back to previous page
    window.history.back();
}