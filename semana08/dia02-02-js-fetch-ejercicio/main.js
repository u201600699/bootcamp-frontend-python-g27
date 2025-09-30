// DOCUMENTACIÓN: https://web.dragonball-api.com/



// API: https://dragonball-api.com/api/characters

const url = 'https://dragonball-api.com/api/characters'

const renderCharacters = (characters) => {
  const appDiv = document.querySelector('#app')

  let html = ''

  characters.forEach(character => {
    html += `
      <article>
        <h2>${character.id} - ${character.name}</h2>
        <img src="${character.image}" height="200" />
      </article>
    `
  });

  appDiv.innerHTML = html
}

fetch(url)
  .then(response => response.json())
  .then(data => {
    // console.log(data)
    
    renderCharacters(data.items)
  })


  
// TODO: Renderizar los nombres de los planetas de la siguiente ruta (API) y mostrar su nombre, descripción y su imagen


const url_planetas= 'https://dragonball-api.com/api/planets'

const renderPlanetas = (planeta) =>{
const DivPlanetas = document.querySelector('#planetas')
let html_planetas = ''

planeta.forEach(plan =>{
    html_planetas += `
      <article>
        <h2>${plan.id} - ${plan.name}</h2>
        <p> ${plan.description} </p>
        <img src="${plan.image}" height="200" />
      </article>
    `
});

DivPlanetas.innerHTML = html_planetas

}

fetch(url_planetas)
.then(response => response.json())
.then(data =>{
    renderPlanetas(data.items)
})