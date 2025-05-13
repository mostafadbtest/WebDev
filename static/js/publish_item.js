
const uploadForm      = document.getElementById('upload-form');
const uploadButton    = document.getElementById('upload-button');
const fileInput       = document.querySelector('.file-input');
const imagesContainer = document.getElementById('images');
const publishForm     = document.getElementById('publish-form');

//--------------------------------------------------------------

async function fetchAndApplyMixHtml(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      ...(options.headers || {})
    }
  });
  const text = await response.text();
  updatePageWithMixHtmlChanges(text);
  return response;
}

//--------------------------------------------------------------
function updatePageWithMixHtmlChanges(htmlStringFromServer) {
  const htmlDocument = new DOMParser().parseFromString(htmlStringFromServer, "text/html");
  htmlDocument.querySelectorAll("mixhtml").forEach(htmlBlock => {
    if (htmlBlock.hasAttribute("mix-append")) {
      const target = document.querySelector(htmlBlock.getAttribute("mix-append"));
      if (target) {
        if (htmlBlock.innerHTML.includes('class="toast error"')) {
          const errorDiv = htmlBlock.querySelector('.toast.error');
          if (errorDiv) {
            showToast(errorDiv.textContent, 'error');
          } else {
            const match = htmlBlock.innerHTML.match(/<div class="toast error">(.*?)<\/div>/);
            if (match && match[1]) {
              showToast(match[1], 'error');
            } else {
              target.innerHTML += htmlBlock.innerHTML;
            }
          }
        } else {
          target.innerHTML += htmlBlock.innerHTML;
        }
      }
    }
    else if (htmlBlock.hasAttribute("mix-remove")) {
      const selector = htmlBlock.getAttribute("mix-remove");
      document.querySelectorAll(selector)
              .forEach(node => node.remove());
    }
    else if (htmlBlock.hasAttribute("mix-replace")) {
      const target = document.querySelector(htmlBlock.getAttribute("mix-replace"));
      if (target) target.innerHTML = htmlBlock.innerHTML;
    }
  });
  hideToastsAfterDelay();
}

// --------------------------------------------------------------
document.addEventListener("click", event => {
  if (!event.target.matches("[mix-delete]")) return;
  event.preventDefault();
  const url = event.target.getAttribute("mix-delete");
  fetchAndApplyMixHtml(url, { method: "DELETE" })
    .catch(err => console.error("Delete failed:", err));
});

// --------------------------------------------------------------
if (uploadForm && uploadButton && fileInput && imagesContainer) {
  uploadButton.addEventListener('click', function() {
    if (fileInput.files.length === 0) {
      showToast('Please select at least 2 image before uploading', 'error');
      return;
    }

    const formData = new FormData(uploadForm);

    uploadButton.disabled   = true;
    uploadButton.textContent = 'Uploading...';

    // Send AJAX request
    fetch('/add-item', {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(response => {
        if (!response.ok) {
          return response.text().then(text => { throw new Error(text); });
        }
        return response.text();
      })
      .then(html => {

        updatePageWithMixHtmlChanges(html);
        uploadForm.reset();
      })
      .catch(error => {
        let errorMessage = error.message;
        const match = errorMessage.match(/<div class="toast error">(.*?)<\/div>/);
        if (match && match[1]) {
          errorMessage = match[1];
        }
        showToast(errorMessage, 'error');
      })
      .finally(() => {
        uploadButton.disabled   = false;
        uploadButton.textContent = 'Upload Images';
      });
  });
}

// --------------------------------------------------------------
function selectImage(imagePk) {
  document.getElementById('selected_image_pk').value = imagePk;
  // Visually highlight the selected image (added for better UX)
  document.querySelectorAll('.image-card').forEach(card => {
    card.classList.remove('selected');
  });
  const selectedCard = document.getElementById('x' + imagePk);
  if (selectedCard) {
    selectedCard.classList.add('selected');
  }
}
window.selectImage = selectImage;

// --------------------------------------------------------------
function showToast(message, type = 'success') {
  // Create toast element
  const toast = document.createElement('div');
  toast.className   = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 500);
  }, 3000);
}

// --------------------------------------------------------------
function hideToastsAfterDelay() {
  document.querySelectorAll('.toast').forEach(toast => {
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 500);
    }, 3000);
  });
}

// --------------------------------------------------------------
if (publishForm) {
  publishForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const selectedImagePk = document.getElementById('selected_image_pk').value;
    if (!selectedImagePk) {
      showToast('Please select an image', 'error');
      return;
    }
  
    const formData = new FormData(publishForm);
    // Send AJAX request
    fetch('/publish-item', {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(response => {
        if (!response.ok) {
          return response.text().then(text => { throw new Error(text); });
        }
        
        showToast('Item published successfully!', 'success');
       
        document.getElementById('item_name').value  = '';
        document.getElementById('item_price').value = '';
        document.getElementById('item_lon').value   = '';
        document.getElementById('item_lat').value   = '';
        document.getElementById('selected_image_pk').value = '';

        document.querySelectorAll('.image-radio').forEach(radio => radio.checked = false);
        document.querySelectorAll('.image-card').forEach(card => card.classList.remove('selected'));
        return null; 
      })
      .catch(error => {
        let errorMessage = error.message;
        const match = errorMessage.match(/<div class="toast error">(.*?)<\/div>/);
        if (match && match[1]) errorMessage = match[1];
        showToast(errorMessage, 'error');
      });
  });
}
