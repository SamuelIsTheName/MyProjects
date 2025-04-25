//
//  ContentView.swift
//  LightRemote
//
//  Created by SAMUEL on 24/11/2023.
//

import SwiftUI

struct ContentView: View {
    @State private var on = true
    var body: some View {
        VStack {
            if on{
                Label(" ", systemImage: "lightbulb.max")
                                .font(.system(size:32))
                                .imageScale(.large)
            }
            
            
            Button(action:{
                if(on == true)
                {
                    on = false
                }else{
                    on = true
                }
                onOff(oN: self.on)
                
            }
            ){
                Label("On/Off", systemImage: "power")
                    .padding()
                    .font(.system(size: 30))
                    .foregroundColor(.white)
                    .background(Color.red)
                    .cornerRadius(60)
            }
            if on{
                Scroller().padding()
                ColorPickerView()
            }
           
            
        }
        .padding()
    }
}
func onOff(oN : Bool)
{
    let lightID = "b39673d2-5492-419e-a4e2-c8b2f7c2ed04"
        let urlString = "https://add ip-address/clip/v2/resource/light/\(lightID)"
        
        guard let url = URL(string: urlString) else {
            print("Invalid URL")
            return
        }
        
        // create the request
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        
        
        request.setValue("add application key", forHTTPHeaderField: "hue-application-key")
        
        
        let bodyData: [String: [String: Bool]] = ["on": ["on": oN]]
        guard let requestBody = try? JSONSerialization.data(withJSONObject: bodyData) else {
            print("Error creating request body")
            return
        }
        
        request.httpBody = requestBody
        
        let delegate = CustomSessionDelegate()
        let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
        
        let task = session.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                return
            }
            
            
            if let httpResponse = response as? HTTPURLResponse {
                print("Response status code: \(httpResponse.statusCode)")
                
                if let responseData = data{
                    do{
                        let decoder = JSONDecoder()
                        let response = try decoder.decode(HueLightControllerResponse.self, from: responseData)
                        
                        if let firstLightData = response.data.first{
                            print("Light ID: \(firstLightData.rid)")
                            print("Light Type: \(firstLightData.rtype)")
                        }
                        if response.errors.isEmpty{
                            print("Request successful")
                        }else{
                            print("Errors occured: \(response.errors)")
                        }
                    }catch{
                        print("Error decoding response: \(error)")
                    }
                }
            }
        }
        
        task.resume()
}

#Preview {
    ContentView()
}
