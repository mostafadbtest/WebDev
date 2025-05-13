// Instant search results
const search_results = document.querySelector("#search_results");
const input_search   = document.querySelector("#input_search");
let my_timer = null;

function search(){
  clearInterval(my_timer);
  if (input_search && input_search.value !== "") {
    my_timer = setTimeout(async function(){
      try {
        const search_for = input_search.value;
        const conn       = await fetch(`/search?q=${encodeURIComponent(search_for)}`);
        const data       = await conn.json();

        search_results.innerHTML = "";
        data.forEach(item => {
          let imageSrc = "";
          if (item.item_image.includes('/')) {
            imageSrc = `/static/${item.item_image}`;
          } else if (['1.jpg','2.jpg','3.jpg','4.jpg','5.jpg','default.jpg']
                      .includes(item.item_image)) {
            imageSrc = `/static/images/${item.item_image}`;
          } else {
            imageSrc = `/static/uploads/${item.item_image}`;
          }

          const a = `
            <div class="instant-item" mix-get="/items/${item.item_pk}">
              <img src="${imageSrc}">
              <a href="/${item.item_name}">${item.item_name}</a>
            </div>`;
          search_results.insertAdjacentHTML("beforeend", a);
        });

        mix_convert();
        search_results.classList.remove("hidden");
      } catch(err) {
        console.error(err);
      }
    }, 500);
  } else if (search_results) {
    search_results.innerHTML = "";
    search_results.classList.add("hidden");
  }
}


addEventListener("click", function(event){
  if (search_results && !search_results.contains(event.target)) {
    search_results.classList.add("hidden");
  }
  if (input_search && input_search.contains(event.target)) {
    search_results.classList.remove("hidden");
  }
});


function add_markers_to_map(data) {
  data = JSON.parse(data);
  data.forEach(item => {
    var customIcon = L.divIcon({
      className: 'custom-marker',
      html: `<div mix-get="/items/${item.item_pk}" class="custom-marker">${item.item_name[0]}</div>`,
      iconSize: [50, 50],
      iconAnchor: [25, 25]
    });
    L.marker([item.item_lat, item.item_lon], { icon: customIcon })
     .addTo(map)
     .openPopup();
  });
}

function onMarkerClick(event) {
  alert("Marker clicked at " + event.latlng);
}



const searchOverlay = document.getElementById('search_overlay');
const inputSearch   = document.getElementById('input_search');

if (inputSearch && searchOverlay) {
  inputSearch.addEventListener('focus', function() {
    searchOverlay.classList.remove('hidden');
  });

  inputSearch.addEventListener('blur', function() {
    setTimeout(() => {
      searchOverlay.classList.add('hidden');
    }, 200);
  });

  // Hide overlay when clicked
  searchOverlay.addEventListener('click', function() {
    searchOverlay.classList.add('hidden');
    inputSearch.blur();
  });

} else {
  console.warn('Search overlay or input not found in the DOM');
}
