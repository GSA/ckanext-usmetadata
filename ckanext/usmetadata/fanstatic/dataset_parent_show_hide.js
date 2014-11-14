/**
 * Created by ykhadilkar on 11/11/14.
 */
$(document).ready(function(){
    $()
    $("#field-is_parent").change(function(){
        $val = $("#field-is_parent").val();
        if($val=="false"){
            $(".control-group-dataset-parent").show();
            //remove current dataset from parent dataset list
            $("#field-parent_dataset option[value='"+$('[name="pkg_name"]').val()+"']").remove();
        }
        if($val=="true"){
            $(".control-group-dataset-parent").hide();
            $("#field-parent_dataset").val("");
        }
    }).change();
});
