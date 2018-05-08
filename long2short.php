
<?php
header("Content-Type: text/html; charset=utf-8");  
$longurl = "https://blog.csdn.net/weiming8517/article/details/51626627";    
$id = "wxf4f7276700dd2748";  
$secret = "7ec26bd26d863d0bf0d232e24fe381c5";  
$url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=".$id."&secret=".$secret."";  
  
$token = getAccessToken($url);  
$data = '{"action":"long2short","long_url":"'.$longurl.'"}';  
$shorturl = "https://api.weixin.qq.com/cgi-bin/shorturl?access_token=".$token."";  
  
$result = httpPost($shorturl,$data);  
// 生成的短链接
$shortArr = json_decode($result);
     
function getAccessToken($url) {  
    // access_token 应该全局存储与更新，以下代码以写入到文件中做示例  
    $data = json_decode(file_get_contents("access_token.json"));  
    if ($data->expire_time < time()) {  
      // 如果是企业号用以下URL获取access_token  
      $output = httpGet($url);  
      $res = (array)json_decode($output);  
      $access_token = $res['access_token'];  
      if ($access_token) {  
        $data->expire_time = time() + 7000;  
        $data->access_token = $access_token;  
        $fp = fopen("access_token.json", "w");  
        fwrite($fp, json_encode($data));  
        fclose($fp);  
        //echo 'access_token.json读写了一次';  
      }  
    } else {  
      $access_token = $data->access_token;  
    }  
    return $access_token;  
  }  
    
  function httpGet($url) {  
    //echo "url = ".$url;  
    $curl = curl_init();  
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);  
    curl_setopt($curl, CURLOPT_TIMEOUT, 500);  
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);  
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);  
    curl_setopt($curl, CURLOPT_URL, $url);  
  
    $res = curl_exec($curl);  
    curl_close($curl);  
    return $res;  
  }  
    
  function httpPost($url,$data){  
        $curl = curl_init();  
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);  
        curl_setopt($curl, CURLOPT_TIMEOUT, 500);  
        curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);  
        curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);  
        curl_setopt($curl, CURLOPT_URL, $url);  
        curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "POST");  
        curl_setopt($curl, CURLOPT_POSTFIELDS, $data);  
  
        $res = curl_exec($curl);  
        curl_close($curl);  
        return $res;  
  }  
    
  ?>  