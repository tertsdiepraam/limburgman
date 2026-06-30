const URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYcli77i_Q8vR0zUyWOWO1J0so4Uq2w2tqXDIXDim6HMD9SDDUqVdtjRvywEPfDl2L2F5oWMVLA8ZV/pub?gid=451128911&single=true&output=tsv";

async function reload() {
  const main = document.querySelector("main");

  const r = await fetch(URL);
  const text = await r.text();

  console.log(text);
  
  const lines = text.split("\n");
  const header = lines[0].split("\t");
  const data_lines = lines.slice(1);

  const data = [];

  for (line of data_lines) {
    const new_data = {}
    const data_fields = line.split("\t");
    for (let i = 0; i < header.length; i++) {
      new_data[header[i].toLowerCase().trim()] = data_fields[i];
    }
    data.push(new_data)
  }

  console.log(data);

  for (datum of data) {
    const h2 = document.createElement("h2");
    h2.innerText = datum.titel;

    const a = document.createElement("a");
    a.href = datum.url;
    a.appendChild(h2);

    main.appendChild(a);
  }

}

window.addEventListener("load", reload);
