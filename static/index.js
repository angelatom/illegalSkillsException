
var addWeight = function(e){
    var list = document.getElementById("weightlist");
    var child = list.getElementsByTagName("li")[0];
    var copy = child.cloneNode(true);
    list.appendChild(copy);
};

var removeWeight = function(e){
    var list = document.getElementById("weightlist");
    console.log(list.childNodes.length)
    if (list.childNodes.length > 3){
        list.removeChild(list.lastChild);
    };
};

var add = document.getElementById("addweight");
var remove = document.getElementById("removeweight");
add.addEventListener('click', addWeight);
remove.addEventListener('click', removeWeight);
