(function ($) {
    "use strict";

    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 40) {
            $('.navbar').addClass('sticky-top');
        } else {
            $('.navbar').removeClass('sticky-top');
        }
    });
    
    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('mouseout', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('mouseout');
            }
        }
        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);
    });


    // Modal Video
    $(document).ready(function () {
        var $videoSrc;
        $('.btn-play').click(function () {
            $videoSrc = $(this).data("src");
        });
        console.log($videoSrc);

        $('#videoModal').on('shown.bs.modal', function (e) {
            $("#video").attr('src', $videoSrc + "?autoplay=1&amp;modestbranding=1&amp;showinfo=0");
        })

        $('#videoModal').on('hide.bs.modal', function (e) {
            $("#video").attr('src', $videoSrc);
        })
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Facts counter
    $('[data-toggle="counter-up"]').counterUp({
        delay: 10,
        time: 2000
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        margin: 45,
        dots: true,
        loop: true,
        center: true,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });
    
})(jQuery);

// In your bakers-lovers.js or main.js file

document.addEventListener('DOMContentLoaded', function() {
    // Favorites toggle functionality
    const favoriteButtons = document.querySelectorAll('.favourite-btn');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-id');
            const formId = this.getAttribute('data-form');
            const icon = this.querySelector('i');
            
            // Send AJAX request
            fetch(`/favorites/toggle/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.favourited) {
                        icon.classList.remove('fa-heart-o', 'fa-heart');
                        icon.classList.add('fa-heart', 'text-danger');
                        // Optional: show a success message
                        showToast('Added to favorites!', 'success');
                    } else {
                        icon.classList.remove('fa-heart', 'text-danger');
                        icon.classList.add('fa-heart-o');
                        // Optional: show a success message
                        showToast('Removed from favorites', 'info');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Fallback: submit the form normally if AJAX fails
                document.getElementById(formId).submit();
            });
        });
    });
    
    // Helper function to show toast notifications
    function showToast(message, type = 'info') {
        // Check if toast container exists
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
            document.body.appendChild(toastContainer);
        }
        
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `alert alert-${type} alert-dismissible fade show`;
        toast.role = 'alert';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                toastElement.remove();
            }
        }, 3000);
    }
});

// In your JavaScript for handling favorite button clicks
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// When making fetch request to /favorites/toggle/<product_id>
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json'
    }
})

// ♥ WISH-LIST TOGGLE with improved UX
$(document).on('submit', 'form:has(.wishlist-btn)', function (e) {
    e.preventDefault();
    var form = $(this);
    var btn = form.find('.wishlist-btn');
    var icon = btn.find('i');
    var text = btn.find('.wishlist-text');
    
    // Show loading state
    btn.prop('disabled', true);
    icon.removeClass('fa-heart far fa-heart').addClass('fa-spinner fa-spin');
    
    $.ajax({
        url: form.attr('action'),
        type: 'POST',
        data: form.serialize(),
        success: function(res) {
            if (res.favorited) {
                // Add to wishlist state
                icon.removeClass('fa-spinner fa-spin').addClass('fas fa-heart text-danger');
                text.text('In Wishlist');
                btn.addClass('active').attr('title', 'Remove from wishlist');
                
                // Show success message
                showToast('Added to wishlist!', 'success');
            } else {
                // Remove from wishlist state
                icon.removeClass('fa-spinner fa-spin').addClass('far fa-heart');
                text.text('Add to Wishlist');
                btn.removeClass('active').attr('title', 'Add to wishlist');
                
                // Show success message
                showToast('Removed from wishlist', 'info');
            }
        },
        error: function(xhr) {
            // Reset button state
            if (btn.hasClass('active')) {
                icon.removeClass('fa-spinner fa-spin').addClass('fas fa-heart text-danger');
            } else {
                icon.removeClass('fa-spinner fa-spin').addClass('far fa-heart');
            }
            
            if (xhr.status === 400 && xhr.responseJSON.error) {
                showToast('Error: ' + xhr.responseJSON.error, 'error');
            } else {
                showToast('Error updating wishlist. Please try again.', 'error');
            }
        },
        complete: function() {
            btn.prop('disabled', false);
        }
    });
});

// Simple toast notification function
function showToast(message, type = 'info') {
    var toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Add toast container if not exists
    if (!$('#toastContainer').length) {
        $('body').append('<div id="toastContainer" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    $('#toastContainer').append(toastHtml);
    var toast = new bootstrap.Toast($('#toastContainer .toast').last()[0]);
    toast.show();
}