
fetch("http://localhost:5000/api/actors/36/")
  .then((response) => response.json())
  .then((data) => console.log(data));


