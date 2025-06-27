package com.pulsepath.chat;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
@RestController @RequestMapping("/api/chat") @CrossOrigin(origins="*")
public class ChatController{
  private final RestTemplate http=new RestTemplate();
  @Value("${ai.base-url:http://localhost:6000}") String ai;
  record Msg(String text){}
  @PostMapping("/sentiment")
  public ResponseEntity<String> sentiment(@RequestBody Msg b){
    HttpHeaders h=new HttpHeaders(); h.setContentType(MediaType.APPLICATION_JSON);
    return http.postForEntity(ai+"/sentiment", new HttpEntity<>(b,h), String.class);
  }
}
