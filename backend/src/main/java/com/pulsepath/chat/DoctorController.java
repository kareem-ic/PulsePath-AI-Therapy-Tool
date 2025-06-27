package com.pulsepath.chat;
import com.pulsepath.openai.OpenAiService;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/chat/doctor") @CrossOrigin(origins="*")
public class DoctorController{
  private final OpenAiService ai;
  record Req(String text){} record Res(String reply){}
  DoctorController(OpenAiService ai){this.ai=ai;}
  @PostMapping public Res advise(@RequestBody Req r){ return new Res(ai.chat(r.text())); }
}
