// JavaScript for Civic Issue Reporting System

// Function to handle form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'red';
            isValid = false;
        } else {
            input.style.borderColor = '#ddd';
        }
    });

    return isValid;
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Validate registration form
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateForm('registerForm')) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }

    // Validate login form
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateForm('loginForm')) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }

    // Validate report form
    const reportForm = document.querySelector('form[action*="report"]');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            if (!validateForm('reportForm')) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    }

    // Confirm status update
    const statusForms = document.querySelectorAll('form[action*="update_status"]');
    statusForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to update the status?')) {
                e.preventDefault();
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});

// Function to preview uploaded image
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.createElement('img');
            preview.src = e.target.result;
            preview.style.maxWidth = '200px';
            preview.style.maxHeight = '200px';
            input.parentNode.appendChild(preview);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Add image preview to file input
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            previewImage(this);
        });
    }
});
