// 'use client'

// import CaseList from '@/components/cases/CaseList'
// import NoCasesFound from '@/components/cases/NoCasesFound'
// import { useLoginToken } from '@/hooks/useAuth'
// import { Loader2 } from 'lucide-react'
// import { useSession } from 'next-auth/react'
// import { useRouter } from 'next/navigation'
// import React, { useEffect, useState } from 'react'

// const Dashboard = () => {
//   // const assuranceCases = await fetchAssuranceCases()

//   const [assuranceCases, setAssuranceCases] = useState([])
//   const [isLoggedIn, setIsLoggedIn] = useState<boolean>(true);
//   const [loading, setLoading] = useState(true)

//   const [token] = useLoginToken();
//   const router = useRouter()
//   const { data } = useSession()

//   const fetchAssuranceCases = async (token: any) => {
//     var myHeaders = new Headers();
//     myHeaders.append("Content-Type", "application/json");
//     myHeaders.append("Authorization", `Token ${token}`);

//     var requestOptions: RequestInit = {
//       method: 'GET',
//       headers: myHeaders,
//       redirect: 'follow'
//     };

//     const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/cases/`, requestOptions)

//     if(response.status === 401) {
//       console.log('Invalid Token')
//       localStorage.removeItem('token')
//       router.push('login')
//     }
//     const result = await response.json()
//     return result
//   }

//   useEffect(() => {
//     if(token) {
//       fetchAssuranceCases(token).then(result => {
//         setAssuranceCases(result)
//         setLoading(false)
//       })
//     } else {
//       console.log('No valid token')
//     }
//     // if(token === null) {
//     //   // console.log('No token found')
//     //   // router.push('login')
//     // } else {
//     //   // setIsLoggedIn(token != null);
//     //   fetchAssuranceCases(token).then(result => {
//     //     setAssuranceCases(result)
//     //     setLoading(false)
//     //   })
//     // }
//   },[token])

//   return isLoggedIn ? (
//     <>
//       {loading ? (
//         <div className='flex justify-center items-center min-h-screen'>
//           <div className='flex flex-col justify-center items-center gap-2'>
//             <Loader2 className='w-10 h-10 mt-8 animate-spin' />
//             <p className='text-muted-foreground'>Fetching cases...</p>
//           </div>
//         </div>
//       ) : (
//         <>
//           {token && (
//             <>
//               {assuranceCases && assuranceCases.length === 0 || !assuranceCases ? <NoCasesFound /> : <CaseList assuranceCases={assuranceCases}/>}
//             </>
//         )}
//         </>
//       )}
//     </>
//   ) : null
// }

// export default Dashboard

'use client'

import CaseList from '@/components/cases/CaseList'
import NoCasesFound from '@/components/cases/NoCasesFound'
import { useLoginToken } from '@/hooks/useAuth'
import { Loader2 } from 'lucide-react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import React, { useEffect, useState } from 'react'

const Dashboard = () => {
  const [assuranceCases, setAssuranceCases] = useState([])
  const [loading, setLoading] = useState(true)

  const [token] = useLoginToken();
  const router = useRouter()
  const { data } = useSession()

  const fetchAssuranceCases = async (token: any) => {
    try {
      const myHeaders = new Headers();
      myHeaders.append("Content-Type", "application/json");
      myHeaders.append("Authorization", `Token ${token}`);

      const requestOptions: RequestInit = {
        method: 'GET',
        headers: myHeaders,
        redirect: 'follow'
      };

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/cases/`, requestOptions)

      if(response.status === 401) {
        console.log('Invalid Token')
        // localStorage.removeItem('token')
        // router.push('login')
        return;
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Failed to fetch assurance cases:", error);
      // router.push('login');
    }
  }

  useEffect(() => {
    const storedToken = token || localStorage.getItem('token');

    if(storedToken) {
      fetchAssuranceCases(storedToken).then(result => {
        setAssuranceCases(result)
        setLoading(false)
      })
    } else {
      console.log('No valid token')
      router.push('login');
    }
  }, [token, router])

  return (
    <>
      {loading ? (
        <div className='flex justify-center items-center min-h-screen'>
          <div className='flex flex-col justify-center items-center gap-2'>
            <Loader2 className='w-10 h-10 mt-8 animate-spin' />
            <p className='text-muted-foreground'>Fetching cases...</p>
          </div>
        </div>
      ) : (
        <>
          {assuranceCases.length === 0 ? <NoCasesFound /> : <CaseList assuranceCases={assuranceCases} />}
        </>
      )}
    </>
  )
}

export default Dashboard
