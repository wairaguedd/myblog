// Main script file for the blog functionality

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-close alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Search form validation
    var searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            var searchInput = this.querySelector('input[name="query"]');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.classList.add('is-invalid');
                return false;
            }
            searchInput.classList.remove('is-invalid');
        });
    }

    // Comment form character counter
    var commentContent = document.querySelector('.blog-comments textarea[name="content"]');
    if (commentContent) {
        var maxLength = 1000;
        var counterElement = document.createElement('small');
        counterElement.className = 'form-text text-muted character-counter';
        counterElement.textContent = '0/' + maxLength + ' characters';
        
        commentContent.parentNode.appendChild(counterElement);
        
        commentContent.addEventListener('input', function() {
            var currentLength = this.value.length;
            counterElement.textContent = currentLength + '/' + maxLength + ' characters';
            
            if (currentLength > maxLength) {
                counterElement.classList.add('text-danger');
                this.classList.add('is-invalid');
            } else {
                counterElement.classList.remove('text-danger');
                this.classList.remove('is-invalid');
            }
        });
    }

    // Scroll to top button
    var scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'btn btn-primary rounded-circle position-fixed';
    scrollBtn.style.bottom = '20px';
    scrollBtn.style.right = '20px';
    scrollBtn.style.display = 'none';
    scrollBtn.style.width = '45px';
    scrollBtn.style.height = '45px';
    scrollBtn.style.zIndex = '1000';
    
    document.body.appendChild(scrollBtn);
    
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });

    // Social sharing functionality
    var shareButtons = document.querySelectorAll('.blog-post-share a');
    shareButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.open(this.href, 'Share', 'width=600,height=400');
        });
    });

    // Confirmation for delete actions
    var deleteButtons = document.querySelectorAll('form[action*="delete"] button[type="submit"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Responsive iframes and embeds in blog post content
    var blogPostContent = document.querySelector('.blog-post-content');
    if (blogPostContent) {
        var iframes = blogPostContent.querySelectorAll('iframe');
        iframes.forEach(function(iframe) {
            var wrapper = document.createElement('div');
            wrapper.className = 'ratio ratio-16x9 my-3';
            iframe.parentNode.insertBefore(wrapper, iframe);
            wrapper.appendChild(iframe);
        });
    }
});
