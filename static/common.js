function showErrMsg(errMsg) {
	$('#reason').text(errMsg);
	$('#errorModal').modal();
}

function showServiceError() {
	$('#reason').text("服务器异常!");
	$('#errorModal').modal();
}

function isUnsignedInteger(a) {
	var reg = new RegExp("^[0-9]*$");
	return reg.test(a);
}

function trim(str) {
	return $.trim(str);
}

function isNullOrEmpty(str) {
	strVal=trim(str);
	if (strVal == '' || strVal == null || strVal == undefined|| strVal.length==0) {
		return true;
	} else {
		return false;
	}
}