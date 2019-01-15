var btn = document.getElementById('clipBtn');
var clipboard = new ClipboardJS(btn);
// btn.tooltip('hide');
var alert = document.getElementById('alertTip');


clipboard.on('success', function(e) {
    console.log(e);
    console.info('Action:', e.action);
    console.info('Text:', e.text);
    console.info('Trigger:', e.trigger);
    alert.style.display = 'block';
    e.clearSelection();
});

clipboard.on('error', function(e) {
    setTooltip(e.trigger, 'Failed!');
    hideTooltip(e.trigger);
});
