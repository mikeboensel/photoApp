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

function handleDeleteImg(e, pk) {
    var target = e.target;

    //Find the container object we will remove if delete is successful. 
    while (target.classList.contains('imgContainer') == false &&
        target.tagName !== "BODY") { //If we get to the body something was wrong...
        target = target.parentElement;
    }

    if (target.tagName !== "DIV" || target.classList.contains('imgContainer') == false)
        target = null;

    $.ajax({
        url: "/gallery/handlePicDelete/", //TODO how does URL change impact this?
        method: "POST",
        data: {
            'pk': pk
        },
        success: function(anything, textStatus, jqXHR) {
            if (target != null)
                $(target).remove();
            console.log(anything);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
        },
        beforeSend: handleCSRF4Ajax

    });

    function handleCSRF4Ajax(xhr, settings) {
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
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }

}

function handlePicLike(){
    //TODO
    console.log("Unimplemented");
}

function handlePicPrivacyChange(){
    //TODO
    console.log("Unimplemented");
}

