//設問の選択肢の有無を種別から判断
function selectboxChange(q_name){
  var div = document.getElementById(q_name);
  var select = document.getElementById("change"+q_name);
  //alert(select.value);
  var choice = document.getElementById("choice"+q_name);
  if (choice == null){
    var choice = document.createElement("div");
    choice.class = "choice";
    choice.id = "choice"+q_name;
  }
  if (select.value == "message"){
    div.id = "message"+q_name.substr(1);
    div.innerHTML = '<br><textarea name="" rows="4" cols="40"></textarea>'+ '<button type="button" onclick=deleteMessage("'+div.id+'")>削除</button>';
    deleteQuestion(q_name);
    div.removeChild(div.children);
  }else if(select.value == "textarea" || select.value == "none" || select.value == "text"){
    choice.innerHTML = '<p></p>';
  }else{
    choice.innerHTML = '<br><button type="button" onclick=createChoice("choice'+q_name+'")>選択肢追加</button>';
  }
  div.appendChild(choice);
}
//作成されたメッセージを削除
function deleteMessage(div){
  document.getElementById(div).parentNode.removeChild(document.getElementById(div));
}
//選択肢の削除
function createChoice(choice_id){
  var div = document.getElementById(choice_id);
  var choice_num = document.createElement("p");
  var num = div.children.length-1
  choice_num.innerHTML = '<p>'+num+': <input type="text" name=""></p>';
  div.appendChild(choice_num);
  //alert(choice.length);
}

//設問の作成（追加）
q_type = ["none","text","radio", "checkbox", "textarea", "message"];
q_text = ["選択してください","入力","ラジオボタン", "チェックボックス","記述","メッセージ"];
questions = [];
function createQuestion(){
  var f = document.getElementById('q');
  var len = questions.length + 1;
  var div = document.createElement('div');
  var q_name = "Q" + String(len);
  div.setAttribute("id", q_name);
  var select =  document.createElement('select');
  select.id = "change"+q_name;
  select.onchange =  new Function('selectboxChange("'+q_name+'")');

  for (var i = 0;  i<q_type.length; i++){
    var option_add = document.createElement('option');
    option_add.setAttribute("value", q_type[i]);
    option_add.innerHTML = q_text[i];
    select.appendChild(option_add);
  }
  div.innerHTML =  '<br><p id="'+q_name.substr(1)+'">'+q_name+':<input type="text" name=""></p>'+ '<button type="button" name="button" onclick=deleteQuestion("'+q_name+'") id="del'+q_name.substr(1)+'">削除</button>';
  div.appendChild(select);
  document.getElementById('q').appendChild(div);
  questions.push(q_name);
}

//設問の削除
function deleteQuestion(q_name){
  var del_node = document.getElementById(q_name);
  try{
    del_node.parentNode.removeChild(del_node);
  }
  catch(ignored){
  }
  questions.pop();
  for (var i in questions){
    if (Number(questions[i].substr(1)) >= Number(q_name.substr(1))){
      var tar = Number(questions[i].substr(1)) + 1;
      var change_node = document.getElementById("Q" + String(tar));
      change_node_id = "Q" + String(tar - 1);
      change_node.id = change_node_id;

      var change_p = document.getElementById(String(tar));
      change_p.innerHTML =  '<p>'+change_node_id+':<input type="text" name="" value=""></p>';
      change_p.id = String(tar - 1);

      var del_button = document.getElementById("del"+String(tar));
      del_button.onclick = new Function('deleteQuestion("'+change_node_id+'")');
      del_button.id = "del" + String(tar - 1);

      var select_id = document.getElementById("changeQ"+String(tar));
      select_id.onchange = new Function('selectboxChange("'+change_node_id+'")');
      select_id.id = "changeQ" + String(tar - 1);

      try{
        var choice_id = document.getElementById("choiceQ"+String(tar));
        var choice_button = choice_id.children[1];
        choice_id.id = "choiceQ" + String(tar - 1);
        choice_button.onclick = new Function('createChoice("'+choice_id.id+'")');
      }catch(ignored){
      }
    }
  }
}

//index.htmlのformデータをJSON型に整理してpage1.phpへPOST
function send_data(){
  var data = {};
  data["site-title"] = document.getElementById('site-title').value;

  var q = document.getElementById('q').children;
  for (var i = 0; i < q.length; i++){
    if (q[i].id ){
      if(q[i].id.substr(0,1) === "Q"){
        data[q[i].id] = {};
        var q_info = q[i].children;
        data[q[i].id]["type"] = q_info[3].value;
        data[q[i].id]["title"] = q_info[1].children[0].value;

        if(q_info[3].value === "textarea"){
          continue;
        }
        if(q_info[4]){
          var choice = q_info[4].children;
          for (var v = 2; v < choice.length ; v++){
            data[q[i].id]["choice"+String(v - 1)] = choice[v].children[0].children[0].value;
          }
        }
      }else{
        data[q[i].id] = q[i].children[1].value;
      }
    }
  }
  var json = JSON.stringify(data);
  var element = document.getElementById('data');
  element.value = json;
  //alert(json);
  document.myform.submit();
}
