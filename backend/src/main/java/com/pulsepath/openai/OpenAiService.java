package com.pulsepath.openai;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Map;
@Service
public class OpenAiService {
  @Value("${openai.key}") private String apiKey;
  private final RestTemplate http = new RestTemplate();
  public String chat(String prompt){
    HttpHeaders h=new HttpHeaders(); h.setBearerAuth(apiKey); h.setContentType(MediaType.APPLICATION_JSON);
    Map<String,Object> body=Map.of("model","gpt-4o-mini","messages",new Object[]{
      Map.of("role","system","content","You are a licensed physician."),
      Map.of("role","user","content",prompt)
    });
    var resp=http.postForEntity("https://api.openai.com/v1/chat/completions",
                                new HttpEntity<>(body,h), Map.class);
    return ((Map<?,?>)((java.util.List<?>)resp.getBody().get("choices")).get(0))
           .get("message").toString();
  }
}
