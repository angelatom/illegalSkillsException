var box, hiddenInput;
var keysDown = {};

var init = function() {
  box = document.getElementById("textEditor");
  hiddenInput = document.getElementById("hiddenInput");
  boxText = box.innerHTML;
  document.execCommand("defaultParagraphSeparator", false, "div");
}

var format = function(cmd) {
  console.log(cmd);
  document.execCommand(cmd);
}

init();

box.addEventListener("keydown", function(event) {
  var ctrlDown = event.ctrlKey;
  var keyPressed = event.which;
  cmd = null;
  if (ctrlDown) {
    switch(keyPressed) {
      case 66: //Check for b pressed
        cmd = "bold";
      case 73: //Check for i pressed
        cmd = "italic";
      case 85: //Check for u pressed
        cmd = "underline";
    }
  }
  format(cmd);
});

box.addEventListener("focusout", function() {
  var inputText = document.getElementById("textEditorInput");
  inputText = inputText.innerHTML;
  hiddenInput.value = inputText;
});
