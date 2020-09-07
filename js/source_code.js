$(window).scroll(function () {
	if($(window).scrollTop() >= $("#code").offset().top){
		$(".code-top").css("display","block");
	}else{
		$(".code-top").css("display","none");
	}
});

var paras = location.search.substring(1).split("&");
var dir = paras[0];
var file = paras[1];

var title = document.getElementById("title");
title.innerHTML = dir;

document.getElementById("img").setAttribute('src', "img/works/"+dir+".jpg");

var httpobj = new XMLHttpRequest();

var about_array = ["lang","time","description","point"];
for (i=0; i<about_array.length; i++){
	httpobj.open('GET',"source/"+dir+"/"+about_array[i]+".txt",false);
	httpobj.send();
	$("#"+about_array[i]).text(httpobj.responseText);
}

httpobj.open('GET',"source/"+dir+"/files.txt",false);
httpobj.send();
var result = httpobj.responseText.split(",");

console.log(httpobj.responseText);
if (result.indexOf(file) >= 0){
	console.log(file);
}

var tabs = document.getElementById("tabList");
for(var i=0; i<result.length; i++){
	var tab = document.createElement("li");
	var tar = result[i];
	tab.id = tar;

	if(i == 0 && file == null){
		tab.className = "tab is-active";
		getCode(tab.id);
	}else if(tar == file){
		tab.className = "tab is-active";
		getCode(tab.id);
		scrollTo(0,$("#source-section").offset().top);
	}else{
		tab.className = "tab";
	}

	tab.innerHTML = tar;
	tabs.appendChild(tab);
};

document.addEventListener('DOMContentLoaded', function(){
    // タブに対してクリックイベントを適用
		const tabs = document.getElementsByClassName('tab');
		for(let i = 0; i < tabs.length; i++) {
        tabs[i].addEventListener('click', tabSwitch);
			}
		function tabSwitch(){
        // タブのclassの値を変更
        	//document.getElementsByClassName('is-active')[0].classList.remove('is-active');
        	//this.classList.add('is-active');
				location.href = 'work.html?'+paras[0]+"&"+this.id;
    	};
});

function getCode(fileName){
	httpobj.open('GET',"source/"+dir+"/"+fileName,false);
	httpobj.send();
	var sourceCode = httpobj.responseText;
	//document.getElementById("code").remove();
	//var dummy = document.getElementById("dummy");
	var outFrame = document.getElementById("code");
	//var outFrame = document.createElement("pre");
	//outFrame.className = "prettyprint linenums";
	//outFrame.id = "code";
	outFrame.innerHTML = sourceCode;
	//dummy.appendChild(outFrame);
};
