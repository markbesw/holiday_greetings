$(document).ready(function () {

  $(".email-alert").click(function () {
    $(this).hide("slow");
  });

  setTimeout(function () {
    $('.email-alert').hide('slow');
  }, 5000
  );
  
  var audio = $(".bgMusic");
  for (let i = 0; i < audio.length; i++){
    audio[i].volume = 0.1;
  }

// audio.autoplay = true;
});



function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function (e) {
      $("#img-preview").attr("src", e.target.result);
    };

    reader.readAsDataURL(input.files[0]); // convert to base64 string
  }
}

$("#file-upload").change(function () {
  readURL(this);
});