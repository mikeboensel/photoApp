Dropzone.options.dropzoneForm = {
  init: function() {
//     this.on("addedfile", function(file) { 
//             console.log("Added file."); 
//             }
//         );
    this.on("success", function(file, resp) { 
        console.log("Success for file." + file + resp);
        for (var addedFile of resp.addedFiles) {
            //TODO update template used
            var newImgContainer = "<div class='col-md-4 imgContainer'><img src='" + addedFile + "' alt='My image' class='img-responsive'/></div>";
            $('#imgRow > div:nth-child(1)').before(newImgContainer);
            } 
        
        $(file.previewElement).fadeOut(5000,'swing', function(){
            $(this).remove();
        });
        }
        );
        
    this.on("error", function(file, errMsg, mbXhr) { 
        console.log("Error file." + file + errMsg + mbXhr); 
    });

    var _this = this;
    
    document.querySelector("button#clear-dropzone").addEventListener("click", function() {
        _this.removeAllFiles();
        // If you want to cancel uploads as well, you
        // could also call _this.removeAllFiles(true);
        
        //TODO check if box empty if so re-add prompt to add files
    });

  }
};


/* CSS transitions on dragging files into dropzone */

var dragAndDropForm = document.getElementById('dropzoneForm');

if(dragAndDropForm){ //Only the user who owns the page is given this field
    [ 'dragover', 'dragenter' ].forEach( function( event )
        {
            dragAndDropForm.addEventListener( event, function()
            {
                dragAndDropForm.classList.add( 'is-dragover' );
            });
        });
    [ 'dragleave', 'dragend', 'drop' ].forEach( function( event )
        {
            dragAndDropForm.addEventListener( event, function()
            {
                dragAndDropForm.classList.remove( 'is-dragover' );
            });
    });
}

//TODO out of place. Temporary. 

function viewFullSize(fullSizeImgURL){
    $("#fullScreenDisplay img")[0].src = fullSizeImgURL;
    //TODO comments
    $("#fullScreenDisplay").removeClass('hidden');
    $("#opacityOverlay").removeClass('hidden');  
}

//Called when opacity overlay is clicked. Sets visibility of #fullScreenDisplay to hidden. Ditto for #opacityOverlay
function dismissFullSize(){
    $("#fullScreenDisplay").addClass('hidden');
    $("#opacityOverlay").addClass('hidden');        
}
