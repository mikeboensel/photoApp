/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

function handlePicDelete(e, pk) {
    var target = e.target;

    //Find the container object we will remove if delete is successful. 
    while (target.classList.contains('imgContainer') === false &&
        target.tagName !== "BODY") { //If we get to the body something was wrong...
        target = target.parentElement;
    }

    if (target.tagName !== "DIV" || target.classList.contains('imgContainer') === false)
        target = null;

    $.ajax({
        url: "/gallery/handlePicDelete/", //TODO how does URL change impact this?
        method: "POST",
        data: {
            'pk': pk
        },
        success: function(anything, textStatus, jqXHR) {
            if (target)
                $(target).remove();
            logFascade(anything);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            logFascade(jqXHR);
        },
        beforeSend: handleCSRF4Ajax

    });
}

function handlePicLike(){
    //TODO
    logFascade("Unimplemented");
}

function handlePicPrivacyChange(){
    //TODO
    logFascade("Unimplemented");
}

function handlePicCommentAction(){
    
    $('#commentSubmissionButton').prop('disabled', true);
  
    var msg = $('#newCommentTextArea').val();
    var pk = $('#fullScreenDisplay').prop('fullScreenedPK');
    if(! msg){ //Must have nonblank input
        $('#commentSubmissionButton').prop('disabled', false);
    }
    else if(pk === null || pk === undefined){
        $('#commentSubmissionButton').prop('disabled', false);
        logFascade("Programming error, did not set full screen PK. Debug");
    }
    else{
     $.ajax({
        url: "/gallery/handlePicCommentAction/",
        method: "POST",
        data: {
            'msg': msg,
            'pk': pk
        },
        success: function(anything, textStatus, jqXHR) {
            logFascade(anything);

            $('#newCommentTextArea').val('');
            $('#commentSubmissionButton').prop('disabled', false);

            //append onto comments
            var commentItem= '<li class="commentItem"><span class="commentUserName">' + $('#currentUserName').val() + 
            '</span><span class="commentContents">'+ anything.msg +'</span></li>';                                
            
            $('#commentList > li:last-child').after(commentItem);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            logFascade(jqXHR);
            $('#commentSubmissionButton').prop('disabled', false);

        },
        beforeSend: handleCSRF4Ajax
        });
    }
    
}


function handleCSRF4Ajax(xhr, settings) {
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
}
    
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function logFascade(msg){
    console.log(msg);
}