function showForm(formType) {
    document.getElementById('create-form').style.display = 'none';
    document.getElementById('edit-form').style.display = 'none';
    document.getElementById('delete-form').style.display = 'none';

    if (formType === 'create') {
        document.getElementById('create-form').style.display = 'block';
    } else if (formType === 'edit') {
        document.getElementById('edit-form').style.display = 'block';
    } else if (formType === 'delete') {
        document.getElementById('delete-form').style.display = 'block';
    }
}