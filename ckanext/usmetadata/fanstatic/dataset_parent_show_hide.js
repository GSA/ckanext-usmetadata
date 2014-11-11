/**
 * Created by ykhadilkar on 11/11/14.
 */
$(document).ready(function(){
    $("#field-is_parent").change(function(){
        $( "select option:selected").each(function(){
            if($(this).attr("value")=="false"){
                $(".control-group-dataset-parent").show();
            }
            if($(this).attr("value")=="true"){
                $(".control-group-dataset-parent").hide();
            }
        });
    }).change();
});
