var corepaper = document.querySelector("#core-paper")
var activeno = 1

const marksboxcheck = document.getElementById('marksboxcheck');
document.addEventListener("DOMContentLoaded", function () {
    // document.querySelector("#addqbox").style.display = "none";
    document
        .querySelector("#addqbtn")
        .addEventListener("click", () => visible_addqbox(1));
    document
        .querySelector("#remqbtn")
        .addEventListener("click", () => visible_addqbox(0)); 
});

function visible_addqbox(view){
    if (view == 1) {
        document.querySelector("#addqbox").style.display = "block";
        document.querySelector('#search-box').addEventListener('input', inputHandler)
    }
    else {
        document.querySelector("#addqbox").style.display = "none";
    }
};

const inputHandler = function(e) {
    document.querySelector("#questionbox").innerHTML = null
    var query = document.querySelector('#search-box').value;
    fetch(`/search/${query}`, {
        method: "PUT"
    })
    .then((response) => response.json())
    .then((result) => {
    // Print result
    result.questions.forEach(question => {
        stringexec = `
        <div class="card-body border">
            <div class="row">
                <div class="col-8">
                    <p>${question.question}</p>
                </div>
                <div class="col-4">
                    <button id="addbtn" type="button" class="inline btn btn-outline-secondary float-right">ADD</button>
                </div>
            </div>
        </div>`
        document.querySelector("#questionbox").innerHTML += stringexec
    });
    // console.log(result.questions[0])

    document.querySelectorAll("#addbtn").forEach((button) => {
        button.onclick = function () {
            questionpar = button.parentElement.parentElement.children[0].children[0].innerHTML;
            console.log(questionpar);
            corepaper.appendChild(document.createElement('div')).textContent=`Q.${activeno} ` + questionpar;
            corepaper.appendChild(document.createElement('p')).textContent="Ans:";
            corepaper.appendChild(document.createElement('br'));
            corepaper.appendChild(document.createElement('br'));
            corepaper.appendChild(document.createElement('br'));
            visible_addqbox(0);
            activeno++;
        };
    });
    });
};

marksboxcheck.addEventListener('change', e => {
    var tablee = document.innerHTML = 
    `<table id="marksbox" class="table table-bordered">
        <tr>
            <td colspan="3">Name: </td>
        </tr>
        <tr>
            <td colspan="3">Roll No: </td>
        </tr>
        <tr>
            <td colspan="3">Class: </td>
        </tr>
        <tr>
            <td colspan="3">Subject: </td>
        </tr>
        <tr>
            <td>Obtained Marks:</td>
            <td>Total Marks:</td>
        </tr>
    </table>
    `
    if(e.target.checked === true) {
      weeb = document.querySelector(".form-check").appendChild(document.createElement("div"));
      weeb.innerHTML += tablee;
    }
    if(e.target.checked === false) {
      document.querySelector("#marksbox").remove();
    }
});

const checkedwe = function(e) {
    console.log("CHGECKEFD");
    
    if (document.querySelector("#marksboxcheck").checked) {
        document.querySelector(".form-check").appendChild(tablee);
    }
}