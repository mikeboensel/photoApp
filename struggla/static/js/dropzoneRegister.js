Dropzone.options.dropzoneForm = {
  init: function() {
    this.on("success", function(file, resp) { 
        console.log("Success for file." + file + resp);
        for (var addedFile of resp.addedFiles) {
            //TODO update template used
            var newImgContainer = "<div class='col-md-4 imgContainer'><img src='" + addedFile + "' alt='My image' class='img-responsive'/></div>";
            
            $('#imgRow').prepend(newImgContainer);
        } 
        
        $(file.previewElement)
            .fadeOut(5000,'swing', 
                function(){
                    $(this).remove();
            });
        });
        
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

function viewFullSize(fullSizeImgURL, pk){
    $("#fullScreenDisplay img")[0].src = fullSizeImgURL;
    //Store value. Can pull for any operations user may decide to do.
    $('#fullScreenDisplay').prop('fullScreenedPK', pk);
    
     $.ajax({
        url: "/gallery/getPicComments/?pic=" + pk,
        method: "GET",
        success: function(anything, textStatus, jqXHR) {
            logFascade(anything);
            //Replacing comment contents
            var c = $("#fullScreenUserCommentsSection");
            c.children().empty();
            c.append(anything);

        },
        error: function(jqXHR, textStatus, errorThrown) {
            logFascade(jqXHR);
        }        
        });

    $("#fullScreenDisplay").removeClass('hidden');
    $("#opacityOverlay").removeClass('hidden');  
}

//Called when opacity overlay is clicked. Sets visibility of #fullScreenDisplay to hidden. Ditto for #opacityOverlay
function dismissFullSize(){
    $("#fullScreenDisplay").addClass('hidden');
    $("#opacityOverlay").addClass('hidden');        
}
