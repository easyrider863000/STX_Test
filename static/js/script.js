function deleteBook(bookId){
    $("#delete-id").val(bookId);
}

function editBook(bookId){
    var editObject = $("#obj-"+bookId).parent().parent();
    $("#edit-id").val(bookId);
    $("#title").val(editObject.find(".title").html());
    $("#linktopicture").val(editObject.find(".picture").prop("src"));
    $("#authors").val(editObject.find(".authors").html());
    $("#isbns").val(editObject.find(".isbns").html());
    $("#countpages").val(editObject.find(".countpages").html());
    $("#language").val(editObject.find(".langname").html());
    $("#publishdate").val(editObject.find(".dateCorrect").val());
}
$(document).ready(function(){
	// Activate tooltip
	$('[data-toggle="tooltip"]').tooltip();

	// Select/Deselect checkboxes
	var checkbox = $('table tbody input[type="checkbox"]');
	$("#selectAll").click(function(){
		if(this.checked){
			checkbox.each(function(){
				this.checked = true;
			});
		} else{
			checkbox.each(function(){
				this.checked = false;
			});
		}
	});
	checkbox.click(function(){
		if(!this.checked){
			$("#selectAll").prop("checked", false);
		}
	});

});