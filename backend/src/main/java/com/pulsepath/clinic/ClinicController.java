package com.pulsepath.clinic;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
@RestController @RequestMapping("/api/clinics") @CrossOrigin(origins="*")
public class ClinicController {
  @Value("${google.places.key}") String key;
  private final RestTemplate http=new RestTemplate();
  @GetMapping
  public String nearby(@RequestParam double lat,@RequestParam double lng,@RequestParam(defaultValue="5000") int radius){
    return http.getForObject(String.format(
      "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%f,%f&radius=%d&type=hospital&key=%s",
      lat,lng,radius,key), String.class);
  }
}
