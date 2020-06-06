// CHAT BOOT MESSENGER///////////////////////


$(document).ready(function(){
    $(".chat_on").click(function(){
        $(".Layout").toggle();
        $(".chat_on").hide(300);
    });
    
       $(".chat_close_icon").click(function(){
        $(".Layout").hide();
        $(".chat_on").show(300);
    });
    
    var socket = io.connect('http://127.0.0.1:5000');

	socket.on('connect', function() {
      //console.log("sooa");
      
	}); 

	socket.on('message', function(msg) {
        //console.log('Received message');
        const div = document.createElement('div');
        if ( (msg=="You") || msg==("Tim") ) {
            //$("#messages").append('<li><strong class="text-primary">'+msg+'</strong></li>' );
            div.innerHTML = '<strong class="text-primary">'+msg+'</strong>'
        }
        else {
        //$("#messages").append('<li>'+msg+'</li>');
        div.innerHTML = msg
        }
		document.getElementById('msg').appendChild(div);
	});

	$('#sendbutton').on('click', function() {
        //console.log('message sent');
		socket.send($('#myMessage').val());
		$('#myMessage').val('');
	}); 


});   