const toast = document.querySelector('.toast');

if (toast) {
    setTimeout(() => {
        toast.style.transition = 'opacity 0.1s ease'; 
        toast.style.opacity = '0';                   
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}
