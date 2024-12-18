using System;
using System.Text.RegularExpressions;
using System.Globalization;
using System.Threading;

namespace Utils
{
    public class Reader
    {
        public static void ChangeGlobalization() 
        {
            Thread.CurrentThread.CurrentCulture = new CultureInfo("fr-CA");
            Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator = ".";
        }
        
        public static long ReadInt(string request)
        {
            Console.Write(request);
            string input = System.Console.ReadLine();
            bool parsed = long.TryParse(input, out long result);
            while (!parsed) {
                Console.WriteLine("Incorrect input, try again");
                Console.Write(request); 
                input = System.Console.ReadLine();
                parsed = long.TryParse(input, out result);
            }
            return result;
        }

        public static double ReadFloat(string request)
        {
            Console.Write(request);
            string input = System.Console.ReadLine();
            // NumberStyles.Float, CultureInfo.InvariantCulture,
            bool parsed = double.TryParse(input, out double result);
            while (!parsed) {
                Console.WriteLine("Incorrect input, try again");
                Console.Write(request); 
                input = System.Console.ReadLine();
                parsed = double.TryParse(input, out result);
            }
            return result;
        }

        
        public static bool ReadBool(string request)
        {
            string[] yes_s = ["yes", "+", "true"];
            string[] no_s  = ["no", "-", "false"];

            Console.Write(request);
            string input = System.Console.ReadLine();
            input = input.ToLower().Trim();

            bool yes = Array.Exists(yes_s, element => element == input);
            bool no  = Array.Exists(no_s,  element => element == input);

            while (!(yes || no)) {
                Console.WriteLine("Incorrect input, try again");
                Console.Write(request);

                input = System.Console.ReadLine();
                input = input.ToLower().Trim();

                yes = Array.Exists(yes_s, element => element == input);
                no  = Array.Exists(no_s,  element => element == input);
            }

            return yes;
        }

    }
}