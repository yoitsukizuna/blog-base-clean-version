const form = document.querySelector('form');

form.addEventListener('submit', function(event) {
    event.preventDefault();
    cur_page = 1;
    const inputValue = document.querySelector('.input').value;
    search = inputValue.trim();

    getImages(search);

    document.querySelector('.input').value = '';
});

const next = document.querySelector('.next');
const prev = document.querySelector('.prev');

let totalResults;
let cur_page = 1;
let search;

const apiKey = "tHgYPr0qIS0VG-SiibRsl7hW7JZMzHFcvITVf3LyZtk";

next.addEventListener('click', () => {
    cur_page += 1;
    getImages(search);
});

prev.addEventListener('click', () => {
    cur_page -= 1;
    getImages(search);
});

function next_prev(pages) {
    next.classList.add('hidden');
    if (cur_page <= pages) {
        next.classList.remove('hidden');
    }

    prev.classList.remove('hidden');
    if (cur_page === 1) {
        prev.classList.add('hidden');
    }
}

async function getImages(input) {
    const results = await searchImages(input);
    next_prev(results.total_pages);
    showImages(results);
}

async function searchImages(searchQuery) {
    const URL = `https://api.unsplash.com/search/photos?query=${searchQuery}&per_page=20&page=${cur_page}&client_id=${apiKey}`;
    const res = await fetch(URL);
    const data = await res.json();

    return data;
}

function showImages(data) {
    const images = document.querySelector('.images');
    images.textContent = '';

    data.results.forEach(img => {
        const url = img.urls.regular;
        const link = img.links.download;
        const likes = img.likes;

        images.insertAdjacentHTML(
            'beforeend',
            `<div>
                <a href="${link}" target="_blank">
                    <div class="image" style="background-image: url(${url});"></div>
                </a>
                <p class="likes">Likes: <span>${likes}</span></p>
            </div>`
        );

    });
};
