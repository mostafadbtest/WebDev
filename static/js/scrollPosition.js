function maintainScrollPosition() {
  const itemsContainer = document.getElementById('items_more');
  const scrollPosition = itemsContainer.scrollTop;

  itemsContainer.dataset.scrollPosition = scrollPosition;

  setTimeout(() => {
    itemsContainer.scrollTop = parseInt(itemsContainer.dataset.scrollPosition || 0);
  }, 100);
}

document.addEventListener('click', function(e) {
  if (e.target && e.target.id === 'button_more_items') {
    maintainScrollPosition();
  }
});