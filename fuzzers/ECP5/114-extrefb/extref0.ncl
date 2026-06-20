::FROM-WRITER;
design top
{
   device
   {
      architecture sa5p00g;
      device LFE5UM5G-45F;
      package CABGA381;
      performance "8";
   }

   comp EXTREF
   {
      logical {
         cellmodel-name EXTREF;
         program "MODE:EXTREFB ";
      }
      site EXTREF0;
   }


   comp DCU
   {
      logical {
         cellmodel-name DCU;
         program "MODE:DCUA ";
      }
      site DCU0;
   }

    signal q_c
   {
      signal-pins
         // drivers
         (EXTREF, REFCLKO),
         // loads
         (DCU, D_REFCLKI);
      ${route}
   }
}
