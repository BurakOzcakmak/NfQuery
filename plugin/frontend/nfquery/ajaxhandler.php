<?php 
    require_once('loghandler.php');
    require_once('nfqueryutil.php');



	if(isset($_POST['getAlerts'])){
		$result = getSubscriptions();
		print($result);
	}
	if(isset($_POST['name'])){
    		$name = $_POST['name'];
        	$result = getSubscriptionDetail($name);
		echo($result);
        	//echo $result;
    }
	if(isset($_POST['button_status'])){
		editRememberFile();
	}
	if(isset($_POST['checkQueryStatus'])){
		checkQueryStatus();
	}	
	if(isset($_POST['runQueries'])){
		session_start();
		runQueries($_POST['runQueries']);
	}
	if(isset($_GET['getStatisticsOfSubscription'])){
		getStatisticsOfSubscription($_GET['subscriptionName']);
	}
	if(isset($_GET['getOutputOfSubscription'])){
		getOutputOfSubscription($_GET['subscriptionName']);
	}

?>
