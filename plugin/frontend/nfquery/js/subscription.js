var timerId;

function subscription_toggle(button){
	var button_status = 'Off';
	if (button.attr('checked')){
		button_status = 'On';
	}
	//Send button status to be persistence
<<<<<<< HEAD
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",
=======
	$.post("plugins/nfquery/ajaxhandler.php",
>>>>>>> devel
		{
			button_status: button_status,
			button_id: button.attr('id')
		},
	   	function(){}	
	);
}

function getSubscriptionDetail3(name){
<<<<<<< HEAD
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
=======
	$.post("plugins/nfquery/ajaxhandler.php",{ name: name},function(data){
>>>>>>> devel
		$(".collapse").collapse();
                $("#subscription_details").html(data);
  
                $('.mandatory_query_popover').popover({
                	title: "Mandatory Query",
                	content: "Click Here to See Optional Queries Of This Mandatory Query"
        	  });
		  $('.optional_query_popover').popover({
                	title: "Optional Query",
                	content: "This is optional query."
       		  });
		 $('.upDown').click(function (){
                  changeCollapseIcon($(this));
        	 });


	
	} 
	);
}

function runQueries(){
	var subscriptions = $('#subscripted').val() || [];
	subscriptions = subscriptions.join(',');
<<<<<<< HEAD
	$.post("/nfsen/plugins/nfquery/ajaxhandler.php", {run:1, subscriptions: subscriptions}, function(data){ 
=======
	$.post("plugins/nfquery/ajaxhandler.php", {run:1, subscriptions: subscriptions}, function(data){ 
>>>>>>> devel
		//alert(data);
	 });
}

function markMandatoryQueries(button, category){
	var subscriptionName = button.attr('name');
	if(button.attr('checked')){
		$('#' + subscriptionName).find('.mandatory_filter').attr('checked', true);
	}else if(!button.attr('checked')){
		$('#' + subscriptionName).find('.mandatory_filter').attr('checked', false);
	}
}

<<<<<<< HEAD
function getFilters(){
    var isNull = true;
	var queryMap = {};
=======
function getFilters(button){
    var isNull = true;
	var queryMap = {};
    
    button.html("Running <img style='width:20px;height:20px' src='plugins/nfquery/img/loading.gif'>");
>>>>>>> devel
	queryMap['queries'] = {};
    
	$('#queryDiv .accordion-body').each(function(){
		subscriptionName = $(this).attr('id');
		queryMap['queries'][subscriptionName] = {};
<<<<<<< HEAD
		queryMap['queries'][subscriptionName]['mandatory'] = []
		queryMap['queries'][subscriptionName]['optional'] = []
=======
		queryMap['queries'][subscriptionName]['mandatory'] = [];
		queryMap['queries'][subscriptionName]['optional'] = [];
>>>>>>> devel
		$(this).find('.mandatory_filter').each(function(){
			if($(this).attr('checked')){
                isNull = false;
				queryMap['queries'][subscriptionName]['mandatory'].push($(this).attr('name'));
			}
		});

		$(this).find('.optional_filter').each(function(){
			if($(this).attr('checked')){
                isNull = false;
				queryMap['queries'][subscriptionName]['optional'].push($(this).attr('name'));
			}
		});
	});

	//send them to the server.
	source = $('#flowSource').val();
    if (isNull){
       alert("Select a Query First !");
<<<<<<< HEAD
    }else{
	    $.post('/nfsen/plugins/nfquery/ajaxhandler.php', {runQueries:queryMap, source:source}, function(data){});
	    	
=======
       button.html("Run !");
    }else{
	  //$.post('plugins/nfquery/ajaxhandler.php', {runQueries:queryMap, source:source}, function(data){});
	  //Sync post solves the problem
        $.ajax({
           type: "POST",
           url: "plugins/nfquery/ajaxhandler.php",
           data: {runQueries:queryMap, source:source},
           async: false
           }).done(function() {
           }
        );  	
>>>>>>> devel
	    $('#nfqueryTab').val('Running');
	    $('#navigationForm').submit();
    }

}

<<<<<<< HEAD
=======
function go(){
            $('#nfqueryTab').val('Running');
	    $('#navigationForm').submit();


}
>>>>>>> devel
function changeCollapseIcon(column){
	var icon = column.find('i');
	if (icon.hasClass('icon-chevron-down')){
		icon.removeClass('icon-chevron-down');
		icon.addClass('icon-chevron-up');
	}else{
		icon.removeClass('icon-chevron-up');
		icon.addClass('icon-chevron-down');
	}
}

$(document).ready(function() {

	$('.subscription_toggle').iphoneStyle({
		checkedLabel: 'On',
		uncheckedLabel: 'Off',
		onChange: function(elem, value){
			subscription_toggle(elem);
		}
	});  

	$('.markAllMandatory').click(function() {
		markMandatoryQueries($(this), 'optional');
	}); 

	$('.nfqueryNav').click(function(){
		var tabName = $(this).text();
		$('#nfqueryTab').val(tabName);
		$('#navigationForm').submit();
	});
	
	//At least one flow source must be selected.Set First One Default here.
	$("#flowSource option:first").attr('selected','selected');

	$(".collapse").collapse();
<<<<<<< HEAD
	$('#runQueries').click(getFilters);
=======
	$('#runQueries').click(function(){
            getFilters($(this));
    });
>>>>>>> devel
	
	$('.mandatory_query_popover').popover({
		title: "Mandatory Query",
		content: "Click Here to See Optional Queries Of This Mandatory Query"
	});

	$('.optional_query_popover').popover({
		title: "Optional Query",
		content: "This is optional query."
	});

	$('.upDown').click(function (){
		changeCollapseIcon($(this));
	});
});
