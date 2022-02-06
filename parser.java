package chomsky;



import java.io.FileReader;



import org.json.JSONArray;

import org.json.JSONObject;

import org.json.JSONTokener;



public class Chomsky {



	public static void main(String args[]) {

		if (args.length != 1) {

			System.out.println("Usar: java Chomsky [GLC]");

			return;

		}



		String filename = args[0];



		try (FileReader reader = new FileReader(filename)) {

            JSONTokener tokener = new JSONTokener(reader);

            JSONObject object = new JSONObject(tokener);

            JSONArray array = object.getJSONArray("glc");

            

            JSONArray states = array.getJSONArray(0);

            JSONArray symbols = array.getJSONArray(1);

            JSONArray transitions = array.getJSONArray(2);

            String start = array.getString(3);

            

            System.out.println(states.toString());

            System.out.println(symbols.toString());

            System.out.println(transitions.toString());

            System.out.println(start.toString());

		} catch (Exception e) {

			e.printStackTrace();

		}

	}

}