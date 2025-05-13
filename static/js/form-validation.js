function clearError(input) {
    input.classList.remove('input_error');
    
    const toast = document.getElementById('toast');
    if (toast) {
        toast.style.display = 'none';
    }
}

const inputs = document.querySelectorAll('input');
inputs.forEach(input => {
    input.addEventListener('input', function() {
        clearError(this);
    });
});