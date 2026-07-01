const URL = "./articles.json";

async function reload() {
  const main = document.querySelector("main");

  const r = await fetch(URL);
  const articles = await r.json();

  for (article of articles) {
    const img = document.createElement("img");

    const imageLinks = Object.values(article["images"]);
    if (imageLinks.length > 0) {
      img.src = imageLinks[0]["src"];
    }
    img.classList.add("preview-image");

    const h2 = document.createElement("h2");
    h2.innerText = article.titel;

    const a = document.createElement("a");
    a.href = article.url;
    a.appendChild(h2);

    const date = document.createElement("p");
    date.classList.add("date")
    if (article.published) {
      const d = new Date(article.published);
      date.innerText = `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
    } else {
      date.innerText = "unknown";
    }

    const rightDiv = document.createElement("div");
    rightDiv.appendChild(a);
    rightDiv.appendChild(date);
    
    const div = document.createElement("div");
    div.classList.add("article");
    div.appendChild(img);
    div.appendChild(rightDiv);

    main.appendChild(div);
  }

}

window.addEventListener("load", reload);
