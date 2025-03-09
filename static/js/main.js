document.addEventListener('DOMContentLoaded', function() {
    // Radio option selection
    const radioOptions = document.querySelectorAll('.radio-option');
    
    radioOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Get the radio input inside this option
            const radio = this.querySelector('input[type="radio"]');
            
            // Check the radio input
            if (radio) {
                radio.checked = true;
                
                // Remove selected class from all options in the same group
                const name = radio.getAttribute('name');
                document.querySelectorAll(`input[name="${name}"]`).forEach(input => {
                    const parentOption = input.closest('.radio-option');
                    if (parentOption) {
                        parentOption.classList.remove('selected');
                    }
                });
                
                // Add selected class to this option
                this.classList.add('selected');
            }
        });
    });
    
    // Processing page progress updates
    const progressElement = document.getElementById('progress-fill');
    const statusElement = document.getElementById('status-text');
    const detailsElement = document.getElementById('progress-details');
    
    if (progressElement && statusElement) {
        // Function to update progress
        function updateProgress() {
            fetch('/api/progress')
                .then(response => response.json())
                .then(data => {
                    // Update progress bar
                    if (data.progress && data.total) {
                        const percentage = (data.progress / data.total) * 100;
                        progressElement.style.width = `${percentage}%`;
                    }
                    
                    // Update status text
                    if (data.phase) {
                        statusElement.textContent = data.message || `${data.phase}...`;
                    }
                    
                    // Update details
                    if (data.section) {
                        detailsElement.textContent = `Working on: ${data.section}`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching progress:', error);
                });
        }
        
        // Update progress every 2 seconds
        const progressInterval = setInterval(updateProgress, 2000);
        
        // Clear interval when page is unloaded
        window.addEventListener('beforeunload', function() {
            clearInterval(progressInterval);
        });
        
        // Initial update
        updateProgress();
    }
    
    // Form validation
    const articleForm = document.getElementById('article-form');
    
    if (articleForm) {
        articleForm.addEventListener('submit', function(event) {
            const topicInput = document.getElementById('topic');
            
            if (!topicInput.value.trim()) {
                event.preventDefault();
                
                // Show error message
                let errorElement = document.querySelector('.error');
                
                if (!errorElement) {
                    errorElement = document.createElement('div');
                    errorElement.className = 'error';
                    articleForm.prepend(errorElement);
                }
                
                errorElement.textContent = 'Please enter a topic for your article.';
                
                // Focus on the input
                topicInput.focus();
            }
        });
    }
}); 