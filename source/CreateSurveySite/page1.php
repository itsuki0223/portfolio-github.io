<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>サイト管理ページ</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <header>
      <h1>アンケート作成ページ</h1>
    </header>
    <div class="container">
    <?php
      //受け取ったデータをJSONに
      $data = json_decode( $_POST["data"] , true );

      echo "サイト名称：".$data["site-title"]."<br><br>";

      //データ内容をサンプル表示
      foreach ($data as $key => $value) {
        if ($key[0] == "Q"){
            echo "<br>".$key.". ".$value["title"]."<br><br>";
            switch($value["type"]){
              case "none":
                echo "種類を選択していません<br>";
              case "textarea":
                echo '<textarea rows="4" cols="40"></textarea><br>';
              default:
                if($value["type"] == "text"){
                  echo '<input type="text"><br>';
                }else{
                  for($i = 1; $i <= count($value)-2; $i++){
                    echo '<input type='.$value["type"].'>'.$value['choice'.strval($i)].'<br>';
                  }
                }
            }
        }elseif ($key[0] == "m") {
          echo "<br>".$value."<br>";
        }
      }
    ?>

    <br><br>
    <form action=# method="post">
      <input value="戻る" onclick="history.back();" type="button">
      <input type="hidden" name="data" value=<?php echo $_POST["data"]; ?>>
      <input type="submit" value="作成" >
    </form>
      <h1>※デモサンプルは以上です。</h1>
    </div>
  </body>
</html>
